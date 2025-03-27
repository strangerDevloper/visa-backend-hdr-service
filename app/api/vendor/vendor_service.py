# app/api/vendor/vendor_service.py
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.vendor.vendor_types import VendorProfileUpdate, VendorSignup
from app.helpers import auth_utils, email_sender
from ...models.vendor import Vendor
import random
import string

USER_TYPE_VENDOR = "vendor"

def generate_default_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_vendor_by_email(db: Session, email: str):
    return db.query(Vendor).filter(Vendor.email == email).first()

def create_vendor(db: Session, vendor: VendorSignup):
    db_vendor = Vendor(
        **vendor.dict(),
        status="PENDING"
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def approve_vendor(db: Session, vendor_id: int, approved_by: int):
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        return None
    
    default_password = generate_default_password()
    vendor.status = "APPROVED"
    vendor.approved_by = approved_by
    vendor.approved_date = datetime.now()
    vendor.password_hash = auth_utils.get_password_hash(default_password)
    
    db.commit()
    db.refresh(vendor)
    
    # Send approval email
    email_sender.send_vendor_approval_email(vendor.email, default_password)
    
    return vendor

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