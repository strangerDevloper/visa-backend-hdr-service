# app/models/employees.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class EmployeeHdr(Base):
    __tablename__ = "employee_hdr"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String)
    email = Column(String)
    mobile_no = Column(String)
    employee_code = Column(String)
    emp_uid = Column(String)
    active_status = Column(Boolean, default=True)
    is_absent = Column(Boolean, default=False)
    absence_expiry = Column(DateTime, nullable=True) # or DateTime, depending on your needs.
    password_hash = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    created_date = Column(DateTime, server_default=func.now())
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    modified_date = Column(DateTime, onupdate=func.now())

    creator = relationship('EmployeeHdr', remote_side=[employee_id], foreign_keys=[created_by])
    modifier = relationship('EmployeeHdr', remote_side=[employee_id], foreign_keys=[modified_by])