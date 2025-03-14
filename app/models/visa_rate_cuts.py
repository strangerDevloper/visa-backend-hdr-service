# app/models/visa_rate_cuts.py
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class VisaRateCut(Base):
    __tablename__ = "visa_rate_cut"

    visa_rate_cut_id = Column(Integer, primary_key=True, autoincrement=True)
    visa_process_id = Column(Integer, ForeignKey('visa_process_hdr.visa_process_id'), nullable=False)
    process_fee = Column(Integer, nullable=False)
    applicable_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True) # Assuming end_date can be null
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    tax = Column(Integer, nullable=True) # Assuming tax can be null
    is_active = Column(Boolean, default=True)

    visa_process = relationship("VisaProcessHdr")
    creator = relationship("EmployeeHdr")