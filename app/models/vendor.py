# app/models/vendor.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.models.enums import Gender, MaritalStatus
from ..config.database import Base
import enum


class VendorStatus(enum.Enum):
    TEMPORARY = "TEMPORARY"  # New status
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    HOLD = "HOLD"
    BLACKLISTED = "BLACKLISTED"


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100))
    email = Column(String, unique=True, nullable=False)
    contact_no = Column(String(20))
    gender = Column(Enum(Gender))
    dob = Column(DateTime)
    marital_status = Column(Enum(MaritalStatus))
    vendor_code = Column(String(50), unique=True)
    pincode = Column(String(10))
    address = Column(String)
    status = Column(Enum(VendorStatus), default=VendorStatus.PENDING)
    vendor_uid = Column(String, unique=True)
    password_hash = Column(String)
    is_temporary: bool = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    approved_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, server_default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    remarks = Column(String(255), nullable=True)

    # Relationships
    documents = relationship("VendorDocument", back_populates="vendor")
    purchase_orders = relationship("VendorPO", back_populates="vendor")
    approver = relationship("EmployeeHdr", foreign_keys=[approved_by])