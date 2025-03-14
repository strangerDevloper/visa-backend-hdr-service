# app/models/roles.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class RoleHdr(Base):
    __tablename__ = "role_hdr"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String)
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id')) # Updated FK
    created_date = Column(DateTime, server_default=func.now())
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id')) # Updated FK
    modified_date = Column(DateTime, onupdate=func.now())
    role_description = Column(String, nullable=True)
    is_system_role = Column(Boolean, default=False)

    creator = relationship('EmployeeHdr', foreign_keys=[created_by]) # Updated relationship
    modifier = relationship('EmployeeHdr', foreign_keys=[modified_by]) # Updated relationship