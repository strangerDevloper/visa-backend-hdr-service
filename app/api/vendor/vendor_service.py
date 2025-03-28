# app/api/vendor/vendor_service.py
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.vendor.vendor_types import VendorProfileUpdate, VendorSignup, VendorStatus
from app.helpers import auth_utils, email_sender
from app.models.vendor_document import VendorDocument, VerificationStatus
from ...models.vendor import Vendor
import random
import string

USER_TYPE_VENDOR = "vendor"

def generate_default_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_vendor_by_email(db: Session, email: str):
    return db.query(Vendor).filter(Vendor.email == email).first()


def create_vendor_with_documents(db: Session, vendor_data: dict, documents: list):
    """
    Creates vendor along with documents in a transaction
    """
    try:
        # Create vendor
        db_vendor = Vendor(
            **vendor_data,
            status=VendorStatus.PENDING.value
        )
        db.add(db_vendor)
        db.flush()  # Get the vendor_id
        
        # Create documents
        for doc in documents:
            db_doc = VendorDocument(
                vendor_id=db_vendor.vendor_id,
                document_type=doc.document_type,
                document_number=doc.document_number,
                document_path=doc.document_path,
                verification_status=VerificationStatus.PENDING.value
            )
            db.add(db_doc)
        
        db.commit()
        return db_vendor
    except Exception as e:
        db.rollback()
        raise

# In vendor_service.py
def approve_vendor(db: Session, vendor_id: int, approved_by: int):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    if vendor.status == VendorStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Vendor already approved")
    
    default_password = generate_default_password()
    vendor.status = VendorStatus.APPROVED.value
    vendor.approved_by = approved_by
    vendor.approved_date = datetime.now()
    vendor.password_hash = auth_utils.get_password_hash(default_password)
    
    try:
        db.commit()
        email_sender.send_vendor_approval_email(vendor.email, default_password)
        return vendor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to approve vendor")

def update_vendor_profile(db: Session, vendor_id: int, updates: VendorProfileUpdate):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        return None
    
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(vendor, field, value)
    
    db.commit()
    db.refresh(vendor)
    return vendor

def update_login_info(db: Session, vendor_id: int):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if vendor:
        vendor.login_count += 1
        # vendor.last_login = datetime.now()
        db.commit()