# app/api/vendor/vendor_types.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

from app.models.vendor_document import VerificationStatus

class VendorStatus(str, Enum):
    TEMPORARY = "TEMPORARY"  # New status
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    HOLD = "HOLD"
    BLACKLISTED = "BLACKLISTED"

class DocumentTypeEnum(str, Enum):
    AADHAR = "AADHAR"
    PAN = "PAN"
    GST = "GST"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VOTER_ID = "VOTER_ID"
    MOU = "MOU"
    BANK_STATEMENT = "BANK_STATEMENT"
    OTHER = "OTHER"


class UploadDocumentRequest(BaseModel):
    document_type: DocumentTypeEnum
    document_number: str
    s3_key: str


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
    vendor_uid: str


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

class VendorSignupResponse(BaseModel):
    vendor_id: int
    email: str
    status: str
    vendor_code: str
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

class DocumentVerificationRequest(BaseModel):
    verification_remarks: Optional[str] = Field(
        None,
        description="Optional remarks for the document approval",
        example="Document looks valid"
    )

# class DocumentApprovalResponse(BaseModel):
#     document_id: int
#     status: str
#     message: str
#     remarks: Optional[str] = None

class DocumentApprovalResponse(BaseModel):
    document_id: int
    status: str
    message: str
    remarks: Optional[str] = None
    approved_by: int
    approved_at: datetime

# class DocumentRejectResponse(BaseModel):
#     document_id: int
#     status: str
#     message: str
#     remarks: Optional[str] = None

class DocumentRejectResponse(BaseModel):
    document_id: int
    status: str
    message: str
    remarks: str
    rejected_by: int
    rejected_at: datetime

class VendorPersonalDetailsUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_no: Optional[str] = None
    pincode: Optional[str] = None
    address: Optional[str] = None

class VendorSecurityUpdate(BaseModel):
    current_password: str
    new_email: Optional[EmailStr] = None
    new_password: Optional[str] = None

class SecurityUpdateResponse(BaseModel):
    email_updated: bool = False
    password_updated: bool = False
    message: str = "Security information updated successfully"

class PaginatedVendorsResponse(BaseModel):
    items: List[VendorPublic]
    total: int
    page: int
    per_page: int
    total_pages: int

class VendorDocumentResponse(BaseModel):
    vendor_document_id: int
    document_type: DocumentTypeEnum
    document_number: str
    document_path: str
    verification_status: VerificationStatus
    uploaded_at: datetime
    presigned_url: Optional[str] = None
    remarks: Optional[str] = None

class VendorWithDocumentsResponse(VendorPublic):
    documents: List[VendorDocumentResponse]

    class Config:
        from_attributes = True

class VendorStatusUpdateRequest(BaseModel):
    status: VendorStatus
    remarks: Optional[str] = Field(
        None,
        description="Optional remarks for the status change",
        example="All documents verified"
    )

class VendorStatusUpdateResponse(BaseModel):
    vendor_id: int
    status: str
    message: str
    remarks: Optional[str] = None
    updated_by: int
    updated_at: datetime
    temporary_password: Optional[str] = Field(
        None,
        description="Temporary password generated when status changes to APPROVED",
        example="Xk8!9sD2"
    )