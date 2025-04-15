# app/api/vendor/vendor_routes.py
from datetime import datetime
from typing import List
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config.aws import AWSService
from app.core.constants import USER_TYPE_VENDOR
from app.helpers import auth_utils
from app.models.vendor import Vendor, VendorStatus
from app.models.vendor_document import VendorDocument, VerificationStatus
from ..dependencies import CurrentEmployee, CurrentVendor  # Updated imports
from . import vendor_service
from .vendor_types import (
    VendorSignup,
    VendorSignupResponse,
    VendorTemporaryCreate,
    VendorTemporaryResponse,
    VendorToken,
    VendorPublic,
    VendorProfileUpdate,
    VendorApprove
)

router = APIRouter(prefix="/vendors", tags=["vendors"])


# Initialize the AWS Service
aws_service = AWSService()

# @router.post("/signup", response_model=VendorSignupResponse)
# def signup_vendor(
#     vendor: VendorSignup, 
#     db: Session = Depends(get_db)
# ):
#     # Check if vendor exists
#     if vendor_service.get_vendor_by_email(db, vendor.email):
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )
    
#     # Separate main data from documents
#     vendor_data = vendor.model_dump(exclude={"documents"})
#     documents = vendor.documents
    
#     try:
#         new_vendor = vendor_service.create_vendor_with_documents(
#             db, 
#             vendor_data, 
#             documents
#         )
#         return VendorSignupResponse(
#             vendor_id=new_vendor.vendor_id,
#             email=new_vendor.email,
#             status=new_vendor.status,
#             **vendor_data  # Include all other fields
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to create vendor: {str(e)}"
#         )

@router.post("/signup-initial", response_model=VendorTemporaryResponse)
def signup_initial(
    vendor: VendorTemporaryCreate,
    db: Session = Depends(get_db)
):
    # Check if email exists
    if vendor_service.get_vendor_by_email(db, vendor.email):
        raise HTTPException(400, "Email already registered")

    # Generate unique IDs
    vendor_uid = str(uuid.uuid4())
    vendor_code = f"VEND-{datetime.now().strftime('%Y%m%d')}-{vendor_uid[:8].upper()}"

    # Create temporary vendor
    db_vendor = Vendor(
        **vendor.model_dump(),
        vendor_uid=vendor_uid,
        vendor_code=vendor_code,
        status=VendorStatus.TEMPORARY.value,
        is_temporary=True
    )
    
    db.add(db_vendor)
    db.commit()

    return VendorTemporaryResponse(
        vendor_uid=vendor_uid,
        vendor_code=vendor_code
    )

@router.put("/{vendor_uid}/complete-signup", response_model=VendorSignupResponse)
def complete_signup(
    vendor_uid: str,
    documents: List[dict],  # Expects output from upload-documents
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.vendor_uid == vendor_uid).first()
    if not vendor or not vendor.is_temporary:
        raise HTTPException(404, "Temporary vendor not found")

    try:
        # Create document records
        for doc in documents:
            db_doc = VendorDocument(
                vendor_id=vendor.vendor_id,
                document_type=doc["document_type"],
                document_number=doc["document_number"],
                document_path=doc["s3_key"],
                verification_status=VerificationStatus.PENDING.value
            )
            db.add(db_doc)

        # Mark vendor as pending (no longer temporary)
        vendor.is_temporary = False
        vendor.status = VendorStatus.PENDING.value
        db.commit()

        return VendorSignupResponse(
            vendor_id=vendor.vendor_id,
            email=vendor.email,
            status=vendor.status
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))

@router.post("/signin", response_model=VendorToken)
def signin_vendor(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_vendor = vendor_service.get_vendor_by_email(db, form_data.username)
    if not db_vendor or not db_vendor.password_hash:
        raise HTTPException(status_code=401, detail="Account not approved or invalid email")
    
    if not auth_utils.verify_password(form_data.password, db_vendor.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    if db_vendor.status != "APPROVED":
        raise HTTPException(status_code=403, detail="Account not approved yet")
    
    access_token = auth_utils.create_access_token(
        data={"sub": str(db_vendor.vendor_id)},
        user_type=USER_TYPE_VENDOR
    )
    vendor_service.update_login_info(db, db_vendor.vendor_id)
    return VendorToken(access_token=access_token)

@router.post("/approve", response_model=VendorPublic)
def approve_vendor(
    approval: VendorApprove,
    current_employee: CurrentEmployee,  # Only employees can access
    db: Session = Depends(get_db),
):
    
    if not current_employee.employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to approve vendors")
    
    approved_vendor = vendor_service.approve_vendor(
        db, 
        approval.vendor_id, 
        current_employee.employee_id
    )
    if not approved_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return approved_vendor

@router.get("/me", response_model=VendorPublic)
def get_my_profile(
    current_vendor: CurrentVendor  # Only vendors can access
):
    return current_vendor

@router.patch("/me", response_model=VendorPublic)
def update_my_profile(
    updates: VendorProfileUpdate,
    current_vendor: CurrentVendor,  # Only vendors can access
    db: Session = Depends(get_db),
):
    updated_vendor = vendor_service.update_vendor_profile(
        db, 
        current_vendor.vendor_id, 
        updates
    )
    if not updated_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return updated_vendor

@router.post("/{vendor_uid}/upload-documents")
async def upload_vendor_documents(
    vendor_uid: str,
    files: List[UploadFile] = File(...),
    document_types: List[str] = Form(...),
    document_numbers: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Verify vendor exists (temporary or regular)
        vendor = db.query(Vendor).filter(Vendor.vendor_uid == vendor_uid).first()
        if not vendor:
            raise HTTPException(404, "Vendor not found")

        if len(files) != len(document_types) or len(files) != len(document_numbers):
            raise HTTPException(400, "Mismatched file/document info count")

        results = []
        for file, doc_type, doc_number in zip(files, document_types, document_numbers):
            # Generate S3 path: vendors/{vendor_uid}/documents/{doc_type}_{uuid}.ext
            file_ext = file.filename.split('.')[-1].lower()
            s3_key = f"vendors/{vendor_uid}/documents/{doc_type}_{uuid.uuid4()}.{file_ext}"

            # Upload to S3 (using your existing AWS service)
            file.file.seek(0)
            aws_service.s3_client.upload_fileobj(
                file.file,
                aws_service.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'private'  # Set appropriate permissions
                }
            )

            results.append({
                "document_type": doc_type,
                "document_number": doc_number,
                "s3_key": s3_key
            })

        return {"success_count": len(results), "uploads": results}

    except Exception as e:
        raise HTTPException(500, detail=str(e))