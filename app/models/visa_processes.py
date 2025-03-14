# app/models/visa_processes.py
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class VisaProcessHdr(Base):
    __tablename__ = "visa_process_hdr"

    visa_process_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    process_name = Column(String(150), nullable=False)
    visa_code = Column(String(50), nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    country_id = Column(Integer, ForeignKey('country_hdr.country_id'))
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    country_fee = Column(Integer, nullable=False)

    country = relationship("CountryHdr")
    modifier = relationship("EmployeeHdr", foreign_keys=[modified_by])
    creator = relationship("EmployeeHdr", foreign_keys=[created_by])