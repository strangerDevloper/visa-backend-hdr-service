# app/models/visa_process_hdr.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class VisaProcessHdr(Base):
    __tablename__ = "visa_process_hdr"

    visa_process_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    process_name = Column(String(150), nullable=False)
    visa_code = Column(String(50), nullable=False)
    country_fee = Column(Integer, nullable=False)
    visa_description = Column(Text, nullable=True)
    vendor_commission = Column(Numeric(5, 2), nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    country_id = Column(Integer, ForeignKey('country_hdr.country_id'))
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))

    # Relationships
    country = relationship("CountryHdr")
    modifier = relationship("EmployeeHdr", foreign_keys=[modified_by])
    creator = relationship("EmployeeHdr", foreign_keys=[created_by])

    # Relationship to media
    media = relationship("CountryServiceMedia", back_populates="visa_process")