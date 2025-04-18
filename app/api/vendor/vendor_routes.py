# app/api/vendor/vendor_routes.py
from datetime import datetime
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.vendor.vendor_service import VendorService
from app.config.database import get_db
from app.helpers.email_utils import email_sender
from app.config.aws import AWSService
from ..dependencies import CurrentEmployee, CurrentUser, CurrentVendor  # Updated imports
from .vendor_types import (
    DocumentApprovalResponse,
    DocumentRejectResponse,
    DocumentVerificationRequest,
    PaginatedVendorsResponse,
    SecurityUpdateResponse,
    UploadDocumentRequest,
    VendorPersonalDetailsUpdate,
    VendorSecurityUpdate,
    VendorSignup,
    VendorSignupResponse,
    VendorStatus,
    VendorStatusUpdateRequest,
    VendorStatusUpdateResponse,
    VendorTemporaryCreate,
    VendorTemporaryResponse,
    VendorToken,
    VendorPublic,
    VendorProfileUpdate,
    VendorApprove,
    VendorWithDocumentsResponse
)

router = APIRouter(prefix="/vendors", tags=["vendors"])

# Initialize the AWS Service
aws_service = AWSService()
logger = logging.getLogger(__name__)  # Get logger for the current module

@router.post(
    "/temporary",
    response_model=VendorTemporaryResponse,
    summary="Create temporary vendor",
    description="Initial signup without documents to get vendor UID for document upload",
    status_code=201
)
def create_temporary_vendor(
    vendor: VendorTemporaryCreate,
    db: Session = Depends(get_db)
):
    try:
        db_vendor = VendorService.create_temporary_vendor(db, vendor)
        return VendorTemporaryResponse(
            vendor_uid=db_vendor.vendor_uid,
            vendor_code=db_vendor.vendor_code
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create temporary vendor: {str(e)}"
        )

@router.patch(
    "/{vendor_uid}/complete",
    response_model=VendorSignupResponse,
    summary="Complete vendor registration",
    description="Submit required documents to complete registration and change status to PENDING",
    responses={
        400: {"description": "Vendor is not in temporary status"},
        404: {"description": "Vendor not found"},
        422: {"description": "Invalid document type"},
        500: {"description": "Internal server error"}
    }
)
def complete_vendor_signup(
    vendor_uid: str,
    documents: List[UploadDocumentRequest],
    db: Session = Depends(get_db)
):
    """
    Complete vendor signup by:
    1. Validating all documents
    2. Creating document records
    3. Updating vendor status
    
    Returns basic vendor information with success message
    """
    try:
        vendor = VendorService.complete_vendor_signup(db, vendor_uid, documents)
        return VendorSignupResponse(
            vendor_id=vendor.vendor_id,
            email=vendor.email,
            status=vendor.status,
            vendor_code=vendor.vendor_code
        )
    except HTTPException as he:
        # Re-raise known HTTP exceptions
        raise he
    except ValueError as ve:
        # Handle document validation errors
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to complete vendor signup. Please try again later."
        )

@router.get(
    "/",
    response_model=PaginatedVendorsResponse,
    summary="Get filtered and paginated vendors",
    responses={
        200: {"description": "Paginated list of vendors"},
        400: {"description": "Invalid filter parameters"}
    }
)
def get_all_vendors(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    vendor_code: Optional[str] = Query(None, description="Filter by exact vendor code"),
    vendor_uid: Optional[str] = Query(None, description="Filter by exact vendor UID"),
    status: Optional[VendorStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Get paginated vendors with optional filters:
    - name: Partial match on first/last name
    - vendor_code: Exact match
    - vendor_uid: Exact match
    - status: Filter by status
    """
    try:
        vendors, total = VendorService.get_filtered_vendors(
            db=db,
            name=name,
            vendor_code=vendor_code,
            vendor_uid=vendor_uid,
            status=status.value if status else None,
            page=page,
            per_page=per_page
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return PaginatedVendorsResponse(
            items=vendors,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filter parameters: {str(e)}"
        )

@router.get(
    "/{identifier}",
    response_model=VendorWithDocumentsResponse,
    summary="Get vendor by ID, code, or UID",
    responses={
        200: {"description": "Vendor details"},
        404: {"description": "Vendor not found"},
        400: {"description": "Invalid identifier format"}
    }
)
def get_vendor(
    identifier: str,
    db: Session = Depends(get_db)
):
    """
    Get vendor by:
    - Database ID (integer)
    - vendor_code (string starting with VEND-)
    - vendor_uid (UUID string)
    """
    return VendorService.get_vendor_with_documents(aws_service, db, identifier)

@router.post("/signin", response_model=VendorToken)
def signin_vendor(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate vendor and return access token"""
    try:
        vendor = VendorService.authenticate_vendor(db, form_data.username, form_data.password)
        access_token = VendorService.generate_access_token(vendor.vendor_id)
        VendorService.update_login_info(db, vendor.vendor_id)
        return VendorToken(access_token=access_token)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=f"Authentication failed: {str(e)}")

@router.post(
    "/documents/{document_id}/approve",
    response_model=DocumentApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a vendor document",
    responses={
        400: {"description": "Invalid request body"},
        403: {"description": "Not authorized to approve documents"},
        404: {"description": "Document not found"},
        409: {"description": "Document already approved/rejected"},
        500: {"description": "Internal server error"}
    }
)
def approve_vendor_document(
    document_id: int,  # From path parameter
    approval_data: DocumentVerificationRequest,  # From request body
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Approve a specific vendor document. Requires employee privileges.
    
    Parameters:
    - document_id: The ID of the document to approve (from URL path)
    - verification_remarks: Optional remarks about the approval (from request body)
    
    Returns:
        Document approval confirmation with status and metadata
    """
    try:
        if not current_employee.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to approve documents"
            )
        
        result = VendorService.approve_vendor_document(
            db=db,
            document_id=document_id,
            approved_by=current_employee.employee_id,
            remarks=approval_data.verification_remarks
        )
        
        return DocumentApprovalResponse(
            document_id=document_id,
            status=result.verification_status,
            message="Document approved successfully",
            remarks=approval_data.verification_remarks,
            approved_by=current_employee.employee_id,
            approved_at=datetime.now()
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document approval failed"
        )

@router.post(
    "/documents/{document_id}/reject",
    response_model=DocumentRejectResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a vendor document",
    responses={
        400: {"description": "Missing rejection remarks"},
        403: {"description": "Not authorized to reject documents"},
        404: {"description": "Document not found"},
        409: {"description": "Document already processed"},
        500: {"description": "Internal server error"}
    }
)
def reject_vendor_document(
    document_id: int,
    reject_data: DocumentVerificationRequest,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Reject a specific vendor document. Requires employee privileges.
    
    Parameters:
    - document_id: The ID of the document to reject (from URL path)
    - verification_remarks: Mandatory remarks explaining the rejection (from request body)
    
    Returns:
        Document rejection confirmation with status and metadata
    """
    try:
        if not current_employee.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reject documents"
            )
        
        result = VendorService.reject_vendor_document(
            db=db,
            document_id=document_id,
            rejected_by=current_employee.employee_id,
            remarks=reject_data.verification_remarks
        )
        
        return DocumentRejectResponse(
            document_id=document_id,
            status=result.verification_status,
            message="Document rejected successfully",
            remarks=reject_data.verification_remarks,
            rejected_by=current_employee.employee_id,
            rejected_at=datetime.now()
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document rejection failed"
        )
    

@router.patch(
    "/{vendor_id}/status",
    response_model=VendorStatusUpdateResponse,
    status_code=status.HTTP_200_OK
)
def update_vendor_status(
    vendor_id: int,
    status_data: VendorStatusUpdateRequest,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Update vendor status with:
    - Status change validation
    - Password generation for APPROVED status
    - Email notification for all status changes
    """
    try:
        if not current_employee.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update vendor status"
            )

        vendor, temp_password = VendorService.update_vendor_status(
            db=db,
            vendor_id=vendor_id,
            new_status=status_data.status,
            updated_by=current_employee.employee_id,
            remarks=status_data.remarks
        )

        # Prepare response
        response = VendorStatusUpdateResponse(
            vendor_id=vendor.vendor_id,
            status=vendor.status,
            message=f"Vendor status updated to {vendor.status}",
            remarks=status_data.remarks,
            updated_by=current_employee.employee_id,
            updated_at=datetime.now()
        )

        # Add password to response if approved
        if status_data.status == VendorStatus.APPROVED and temp_password:
            response.temporary_password = temp_password

        # Send email notification (don't fail the request if email fails)
        try:
            email_sender.send_status_change_email(
                to_email=vendor.email,
                status=status_data.status.value,
                password=temp_password if status_data.status == VendorStatus.APPROVED else None
            )
        except Exception as email_error:
            logger.error(f"Email sending failed: {str(email_error)}")
            # Continue even if email fails - the status change was successful

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Status update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status update failed"
        )

# Profile Management Routes
# @router.get(
#     "/me",
#     response_model=VendorPublic,
#     summary="Get current vendor profile",
#     description="Retrieve the complete profile of the currently authenticated vendor"
# )
# def get_my_profile(current_vendor: CurrentVendor):
#     """Get authenticated vendor's profile"""
#     print(f"Current Vendor ID: {current_vendor.vendor_id}")
#     return current_vendor

@router.patch(
    "/{vendor_id}/update",
    response_model=VendorPublic,
    summary="Update vendor personal details",
    description="Update basic personal information of the vendor",
    responses={
        400: {"description": "Invalid data provided"},
        500: {"description": "Failed to update profile"}
    }
)
def update_personal_details(
    vendor_id: int,
    updates: VendorPersonalDetailsUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update vendor's personal details including:
    - First name
    - Last name
    - Contact information
    - Address details
    """
    try:
        if hasattr(current_user, "employee_id"):
            # Employee-specific logic: Allow update
            pass
        elif hasattr(current_user, "vendor_id") and current_user.vendor_id == vendor_id:
            # Vendor-specific logic: Allow update if vendor_id matches
            pass
        else:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this vendor's details"
            )

        updated_vendor = VendorService.update_vendor_personal_details(
            db=db,
            vendor_id=vendor_id,
            updates=updates
        )
        return updated_vendor
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update personal details"
        )

@router.patch(
    "/{vendor_id}/security",
    response_model=SecurityUpdateResponse,
    summary="Update security information",
    description="Update sensitive security information like email or password",
    responses={
        400: {"description": "Invalid current password (for vendors only)"},
        500: {"description": "Failed to update security information"}
    }
)
def update_security_info(
    vendor_id: int,
    updates: VendorSecurityUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update security information for both vendors and employees:
    - Vendors: Verify current password before updating
    - Employees: Update without verifying current password
    """
    try:
        if hasattr(current_user, "vendor_id") and current_user.vendor_id == vendor_id:
            # Vendor-specific logic: Verify current password
            print("vendor here")
            result = VendorService.update_vendor_security(
                db=db,
                vendor_id=vendor_id,
                current_password=updates.current_password,
                updates=updates,
                verify_current_password=True
            )
        elif hasattr(current_user, "employee_id"):
            print("employee here")
            # Employee-specific logic: No need to verify current password
            result = VendorService.update_vendor_security(
                db=db,
                vendor_id=vendor_id,
                current_password=None,
                updates=updates,
                verify_current_password=False
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this vendor's security information"
            )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update security information"
        )

@router.post("/{vendor_uid}/upload-documents")
async def upload_vendor_documents(
    vendor_uid: str,
    files: List[UploadFile] = File(...),
    document_types: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    """Upload documents for a vendor"""
    try:
        # Verify vendor exists
        vendor = VendorService.get_vendor_by_vendor_uid(db, vendor_uid)
        if not vendor:
            raise HTTPException(404, "Vendor not found")

        # Upload documents to S3
        uploads = VendorService.upload_documents_to_s3(
            aws_service,
            vendor_uid,
            files,
            document_types,
        )

        return {
            "success": True,
            "count": len(uploads),
            "documents": uploads
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=f"Document upload failed: {str(e)}")