# app/api/vendor/vendor_types.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class VendorStatus(str, Enum):
    TEMPORARY = "TEMPORARY"  # New status
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"

class VendorBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    contact_no: str
    gender: str
    dob: datetime
    marital_status: str
    pincode: str
    address: str


# app/api/vendor/vendor_types.py
class VendorTemporaryCreate(BaseModel):
    """Initial signup without documents"""
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    contact_no: str
    gender: str
    dob: datetime
    marital_status: str
    pincode: str
    address: str

class VendorTemporaryResponse(BaseModel):
    vendor_uid: str
    vendor_code: str

class VendorDocumentCreate(BaseModel):
    document_type: str  # Will map to DocumentType enum
    document_number: str
    document_path: str  # Server-side file path


class VendorCreate(VendorBase):
    pass

class VendorSignup(VendorBase):
    documents: List[VendorDocumentCreate]  # Add documents to signup payload

class VendorSignupResponse(VendorSignup):
    vendor_id: int
    status: str
    message: str = "Vendor signup successful. Waiting for admin approval."
    
    class Config:
        from_attributes = True

class VendorApprove(BaseModel):
    vendor_id: int

class VendorToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class VendorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_no: Optional[str] = None
    pincode: Optional[str] = None
    address: Optional[str] = None

class VendorPublic(VendorBase):
    vendor_id: int
    vendor_code: str
    status: str
    created_date: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
