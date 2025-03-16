# app/models/employee_visa_type_access.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class EmployeeVisaTypeAccess(Base):
    __tablename__ = "employee_visa_type_access"

    access_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    employee_id = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)
    visa_process_id = Column(Integer, ForeignKey('visa_process_hdr.visa_process_id'), nullable=True)
    country_id = Column(Integer, ForeignKey('country_hdr.country_id'), nullable=False) 
    granted_at = Column(DateTime, server_default=func.now())
    granted_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)

    employee = relationship("EmployeeHdr", foreign_keys=[employee_id])
    visa_process = relationship("VisaProcessHdr")
    country = relationship("CountryHdr")
    grantor = relationship("EmployeeHdr", foreign_keys=[granted_by])