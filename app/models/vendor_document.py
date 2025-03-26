# app/models/vendor_document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from ..config.database import Base
import enum

class DocumentType(enum.Enum):
    AADHAR = "AADHAR"
    PAN = "PAN"
    GST = "GST"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VOTER_ID = "VOTER_ID"
    OTHER = "OTHER"

class VerificationStatus(enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class VendorDocument(Base):
    __tablename__ = "vendor_documents"

    vendor_document_id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'))
    document_type = Column(Enum(DocumentType))
    document_number = Column(String(100))
    document_path = Column(String)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    uploaded_at = Column(DateTime, server_default=func.now())
    approved_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="documents")
    approver = relationship("EmployeeHdr", foreign_keys=[approved_by])