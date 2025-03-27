# app/api/vendor/vendor_types.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

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

class VendorCreate(VendorBase):
    pass

class VendorSignup(VendorBase):
    pass

class VendorSignupResponse(BaseModel):
    vendor_id: int
    email: EmailStr
    status: str
    message: str = "Vendor signup successful. Waiting for admin approval."

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
