# app/models/vendor_po.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from ..config.database import Base
import enum 

class POStatus(enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"

class VendorPO(Base):
    __tablename__ = "vendor_po_generation"

    po_generation_id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'))
    po_number = Column(String(50), unique=True)
    amount = Column(Integer)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    status = Column(Enum(POStatus), default=POStatus.DRAFT)
    approved_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, server_default=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    approver = relationship("EmployeeHdr", foreign_keys=[approved_by])