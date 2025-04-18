from datetime import datetime
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from botocore.exceptions import ClientError

from app.core.constants import USER_TYPE_VENDOR
from app.helpers import auth_utils

from .vendor_types import (
    SecurityUpdateResponse,
    VendorPersonalDetailsUpdate,
    VendorPublic,
    VendorSecurityUpdate,
    VendorTemporaryCreate,
    UploadDocumentRequest,
    VendorStatus,
    DocumentTypeEnum,
)
from app.models.vendor import Vendor
from app.models.vendor_document import VendorDocument, VerificationStatus

class VendorService:
    
    @staticmethod
    def create_temporary_vendor(db: Session, vendor_data: VendorTemporaryCreate) -> Vendor:
        """Create a temporary vendor record"""
        if VendorService.get_vendor_by_email(db, vendor_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        vendor_uid = str(uuid.uuid4())
        vendor_code = f"VEND-{datetime.now().strftime('%Y%m%d')}-{vendor_uid[:8].upper()}"
        
        db_vendor = Vendor(
            **vendor_data.model_dump(),
            vendor_uid=vendor_uid,
            vendor_code=vendor_code,
            status=VendorStatus.TEMPORARY.value,
            is_temporary=True
        )
        
        db.add(db_vendor)
        db.commit()
        db.refresh(db_vendor)
        return db_vendor

    @staticmethod
    def complete_vendor_signup(
        db: Session,
        vendor_uid: str,
        documents: List[UploadDocumentRequest]
    ) -> Vendor:
        """Complete vendor signup by adding documents and updating status"""
        vendor = VendorService._get_and_validate_temporary_vendor(db, vendor_uid)
        VendorService._validate_documents(documents)
        VendorService._create_documents(db, vendor.vendor_id, documents)
        VendorService._update_vendor_status(db, vendor)
        return vendor

    @staticmethod
    def get_vendor_by_email(db: Session, email: str) -> Optional[Vendor]:
        """Get vendor by email if exists"""
        return db.query(Vendor).filter(Vendor.email == email).first()
    
    @staticmethod
    def get_approve_vendor_by_email(db: Session, email: str) -> Optional[Vendor]:
        """Get vendor by email if exists and is approved"""
        return db.query(Vendor).filter(
            Vendor.email == email,
            Vendor.status == VendorStatus.APPROVED
        ).first()
    
    @staticmethod
    def _get_and_validate_temporary_vendor(db: Session, vendor_uid: str) -> Vendor:
        """Validate vendor exists and is temporary"""
        vendor = db.query(Vendor).filter(Vendor.vendor_uid == vendor_uid).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        print("Vendor found:", vendor.is_temporary)
        if not vendor.is_temporary:
            raise HTTPException(status_code=400, detail="Vendor is not in temporary status")
        return vendor

    @staticmethod
    def _validate_documents(documents: List[UploadDocumentRequest]):
        """Validate document types with proper error messages"""
        if not documents:
            raise ValueError("At least one document is required")
        
        for doc in documents:
            try:
                DocumentTypeEnum(doc.document_type)
            except ValueError:
                valid_types = [e.value for e in DocumentTypeEnum]
                raise ValueError(
                    f"Invalid document type: {doc.document_type}. "
                    f"Valid types are: {valid_types}"
                )

    @staticmethod
    def _create_documents(
        db: Session,
        vendor_id: int,
        documents: List[UploadDocumentRequest]
    ):
        """Create document records"""
        for doc in documents:
            db_doc = VendorDocument(
                vendor_id=vendor_id,
                document_type=doc.document_type,
                document_number=doc.document_number,
                document_path=doc.s3_key,
                verification_status=VerificationStatus.PENDING.value
            )
            db.add(db_doc)

    @staticmethod
    def _update_vendor_status(db: Session, vendor: Vendor):
        """Update vendor status from TEMPORARY to PENDING"""
        vendor.is_temporary = False
        vendor.status = VendorStatus.PENDING.value
        db.commit()

    @staticmethod
    def authenticate_vendor(db: Session, email: str, password: str) -> Vendor:
        """Authenticate vendor and return token"""
        vendor = VendorService.get_approve_vendor_by_email(db, email)
        if not vendor or not vendor.password_hash:
            raise HTTPException(status_code=401, detail="Account not approved or invalid email")
        
        if not auth_utils.verify_password(password, vendor.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password")

        return vendor

    @staticmethod
    def generate_access_token(vendor_id: int) -> str:
        """Generate JWT token for vendor"""
        return auth_utils.create_access_token(
            data={"sub": str(vendor_id)},
            user_type=USER_TYPE_VENDOR
        )
    
    @staticmethod
    def update_login_info(db: Session, vendor_id: int):
        db_vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
        if db_vendor:
            db_vendor.last_login = datetime.utcnow()
            db_vendor.login_count += 1
            db.commit()
            db.refresh(db_vendor)
        return db_vendor

    @staticmethod
    def upload_documents_to_s3(
        aws_service,
        vendor_uid: str,
        files: List[UploadFile],
        document_types: List[str],
    ) -> List[dict]:
        """Upload documents to S3 and return metadata"""
        if len(files) != len(document_types):
            raise HTTPException(400, "Mismatched file/document info count")

        results = []
        for file, doc_type in zip(files, document_types):
            try:
                # Validate document type
                if not hasattr(DocumentTypeEnum, doc_type):
                    raise HTTPException(400, f"Invalid document type: {doc_type}")

                # Generate S3 key
                file_ext = file.filename.split('.')[-1].lower()
                s3_key = f"vendors/{vendor_uid}/documents/{doc_type}_{uuid.uuid4()}.{file_ext}"

                # Upload to S3
                file.file.seek(0)
                aws_service.s3_client.upload_fileobj(
                    file.file,
                    aws_service.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': file.content_type,
                        'ACL': 'private'
                    }
                )

                results.append({
                    "document_type": doc_type,
                    "s3_key": s3_key
                })
            except ClientError as e:
                raise HTTPException(500, f"AWS upload failed: {str(e)}")
            except Exception as e:
                raise HTTPException(500, f"Document processing failed: {str(e)}")

        return results

    @staticmethod
    def get_vendor_profile(db: Session, vendor_id: int) -> Optional[VendorPublic]:
        """Get vendor profile by ID"""
        return db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    
    @staticmethod
    def get_vendor_by_vendor_uid(db: Session, vendor_uid: str) -> Optional[Vendor]:
        """Get vendor by UID"""
        return db.query(Vendor).filter(Vendor.vendor_uid == vendor_uid).first()

    @staticmethod
    def approve_vendor_document(
        db: Session,
        document_id: int,
        approved_by: int,
        remarks : str = None
    ) -> VendorDocument:
        document: VendorDocument = db.query(VendorDocument).get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        print("Document found:", document.verification_status)
        if document.verification_status == VerificationStatus.VERIFIED.value:  
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already processed"
            )
        
        document.verification_status = VerificationStatus.VERIFIED.value
        document.remarks = remarks
        document.approved_by = approved_by
        document.approved_at = datetime.now()
        
        db.commit()
        return document
    
    @staticmethod
    def reject_vendor_document(
        db: Session,
        document_id: int,
        rejected_by: int,
        remarks : str = None
    ) -> VendorDocument:
        document: VendorDocument = db.query(VendorDocument).get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        print("Document found:", document.verification_status)
        if document.verification_status == VerificationStatus.REJECTED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already Rejected"
            )    
        document.verification_status = VerificationStatus.REJECTED.value
        document.remarks = remarks
        document.approved_by = rejected_by
        document.approved_at = datetime.now()
        
        db.commit()
        return document

    @staticmethod
    def update_vendor_personal_details(
        db: Session,
        vendor_id: int,
        updates: VendorPersonalDetailsUpdate
    ) -> Vendor:
        vendor = db.query(Vendor).get(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(vendor, field, value)
        
        db.commit()
        db.refresh(vendor)
        return vendor

    @staticmethod
    def _build_vendor_query(
        db: Session,
        name: Optional[str] = None,
        vendor_code: Optional[str] = None,
        vendor_uid: Optional[str] = None,
        status: Optional[str] = None
    ):
        """Build the base filtered query"""
        query = db.query(Vendor)
        
        if name:
            query = query.filter(
                (Vendor.first_name.ilike(f"%{name}%")) |
                (Vendor.last_name.ilike(f"%{name}%"))
            )
        if vendor_code:
            query = query.filter(Vendor.vendor_code == vendor_code)
        if vendor_uid:
            query = query.filter(Vendor.vendor_uid == vendor_uid)
        if status:
            query = query.filter(Vendor.status == status)
            
        return query

    @staticmethod
    def get_filtered_vendors(
        db: Session,
        name: Optional[str] = None,
        vendor_code: Optional[str] = None,
        vendor_uid: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[Vendor], int]:
        """
        Get paginated and filtered vendors
        Returns tuple of (vendors, total_count)
        """
        query = VendorService._build_vendor_query(
            db, name, vendor_code, vendor_uid, status
        )
        
        total_count = query.count()
        offset = (page - 1) * per_page
        vendors = query.offset(offset).limit(per_page).all()
        
        return vendors, total_count

    @staticmethod
    def get_vendor_by_identifier(
        db: Session,
        identifier: str
    ) -> Vendor:
        """
        Get vendor by ID, code, or UID
        Raises HTTPException(404) if not found
        """
        try:
            # Try to parse as integer (ID)
            if identifier.isdigit():
                vendor = db.query(Vendor).filter(Vendor.vendor_id == int(identifier)).first()
            # Check if it's a vendor code (starts with VEND-)
            elif identifier.startswith("VEND-"):
                vendor = db.query(Vendor).filter(Vendor.vendor_code == identifier).first()
            # Otherwise treat as vendor_uid (UUID)
            else:
                vendor = db.query(Vendor).filter(Vendor.vendor_uid == identifier).first()
            
            if not vendor:
                raise HTTPException(status_code=404, detail="Vendor not found")
                
            return vendor
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid identifier: {str(e)}"
            )
        
    @staticmethod
    def get_vendor_with_documents(
        aws_service,
        db: Session,
        identifier: str
    ) -> dict:
        """
        Get vendor with documents by ID, code, or UID
        Returns dictionary with vendor and documents
        """
        vendor = VendorService.get_vendor_by_identifier(db, identifier)
        
        documents = db.query(VendorDocument).filter(
            VendorDocument.vendor_id == vendor.vendor_id
        ).all()
        
        documents_with_presigned_url = []
        for doc in documents:
            presigned_url = None
            try:
                presigned_url = aws_service.generate_presigned_url(doc.document_path)
            except ClientError as e:
                print(f"Error generating presigned URL: {str(e)}")
            
            documents_with_presigned_url.append({
                **doc.__dict__,
                "presigned_url": presigned_url
            })
        return {
            **vendor.__dict__,
            "documents": documents_with_presigned_url
        }

    @staticmethod
    def update_vendor_security(
        db: Session,
        vendor_id: int,
        current_password: str,
        updates: VendorSecurityUpdate,
        verify_current_password: bool = True
    ) -> SecurityUpdateResponse:
        vendor : Vendor = db.query(Vendor).get(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        
        response = SecurityUpdateResponse()
        
        # Verify current password if changing password and verification is required
        if updates.new_password:
            if verify_current_password and not auth_utils.verify_password(updates.current_password, current_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            vendor.password_hash = auth_utils.get_password_hash(updates.new_password)
            response.password_updated = True
        
        # Update email if provided
        if updates.new_email:
            vendor.email = updates.new_email
            response.email_updated = True
        
        db.commit()
        return response
    
    @staticmethod
    def update_vendor_status(
        db: Session,
        vendor_id: int,
        new_status: VendorStatus,
        updated_by: int,
        remarks: Optional[str] = None
    ) -> Tuple[Vendor, Optional[str]]:
        """
        Update vendor status with validation
        - For APPROVED status: 
            - Checks all documents are approved
            - Generates temporary password
            - Returns tuple of (vendor, temporary_password)
        - For other statuses: Returns (vendor, None)
        """
        vendor: Vendor = db.query(Vendor).get(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )

        current_status = vendor.status
        temp_password = None

        # Check document approval requirement for APPROVED status
        if new_status == VendorStatus.APPROVED:
            unapproved_docs = db.query(VendorDocument).filter(
                VendorDocument.vendor_id == vendor_id,
                VendorDocument.verification_status != VerificationStatus.VERIFIED.value
            ).count()
            
            if unapproved_docs > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot approve vendor with {unapproved_docs} unapproved documents"
                )

            # Generate temporary password only for APPROVED status
            temp_password = auth_utils.generate_random_password()
            vendor.password_hash = auth_utils.get_password_hash(temp_password)

        # Validate status transition
        valid_transitions = {
            VendorStatus.PENDING: [VendorStatus.APPROVED, VendorStatus.REJECTED, VendorStatus.HOLD],
            VendorStatus.HOLD: [VendorStatus.APPROVED, VendorStatus.REJECTED, VendorStatus.PENDING],
            VendorStatus.TEMPORARY: [VendorStatus.PENDING, VendorStatus.REJECTED],
            VendorStatus.APPROVED: [VendorStatus.SUSPENDED, VendorStatus.REJECTED, VendorStatus.HOLD, VendorStatus.BLACKLISTED],
            VendorStatus.REJECTED: [VendorStatus.PENDING, VendorStatus.HOLD],
        }

        if current_status in valid_transitions and new_status not in valid_transitions[current_status]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from {current_status.value} to {new_status.value}"
            )

        # Update status and tracking fields
        vendor.status = new_status
        vendor.modified_date = datetime.now()
        
        if new_status == VendorStatus.APPROVED:
            vendor.approved_by = updated_by
            vendor.approved_date = datetime.now()
        
        if remarks:
            vendor.remarks = remarks

        db.commit()
        db.refresh(vendor)
        return vendor, temp_password

    @staticmethod
    def get_vendor_document_status(vendor_id: int, db: Session) -> dict:
        """Get counts of documents by status for a vendor"""
        status_counts = db.query(
            VendorDocument.verification_status,
            func.count(VendorDocument.vendor_document_id)
        ).filter(
            VendorDocument.vendor_id == vendor_id
        ).group_by(
            VendorDocument.verification_status
        ).all()
        
        return dict(status_counts)