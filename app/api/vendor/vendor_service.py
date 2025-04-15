from datetime import datetime
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional
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
        vendor = VendorService.get_vendor_by_email(db, email)
        if not vendor or not vendor.password_hash:
            raise HTTPException(status_code=401, detail="Account not approved or invalid email")
        
        if not auth_utils.verify_password(password, vendor.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        if vendor.status != VendorStatus.APPROVED.value:
            raise HTTPException(status_code=403, detail="Account not approved yet")
        
        return vendor

    @staticmethod
    def generate_access_token(vendor_id: int) -> str:
        """Generate JWT token for vendor"""
        return auth_utils.create_access_token(
            data={"sub": str(vendor_id)},
            user_type=USER_TYPE_VENDOR
        )

    @staticmethod
    def upload_documents_to_s3(
        aws_service,
        vendor_uid: str,
        files: List[UploadFile],
        document_types: List[str],
        document_numbers: List[str]
    ) -> List[dict]:
        """Upload documents to S3 and return metadata"""
        if len(files) != len(document_types) or len(files) != len(document_numbers):
            raise HTTPException(400, "Mismatched file/document info count")

        results = []
        for file, doc_type, doc_number in zip(files, document_types, document_numbers):
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
                    "document_number": doc_number,
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
    def approve_vendor_document(
        db: Session,
        document_id: int,
        approved_by: int
    ) -> VendorDocument:
        document = db.query(VendorDocument).get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.verification_status != VerificationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already processed"
            )
        
        document.verification_status = VerificationStatus.VERIFIED.value
        document.approved_by = approved_by
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
    def update_vendor_security(
        db: Session,
        vendor_id: int,
        current_password: str,
        updates: VendorSecurityUpdate
    ) -> SecurityUpdateResponse:
        vendor = db.query(Vendor).get(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found"
            )
        
        response = SecurityUpdateResponse()
        
        # Verify current password if changing password
        if updates.new_password:
            if not auth_utils.verify_password(updates.current_password, current_password):
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