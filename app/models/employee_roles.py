# app/models/employee_roles.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class EmployeeRole(Base):
    __tablename__ = "employee_role"

    employee_role_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role_hdr.role_id'), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())
    assigned_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)

    employee = relationship("EmployeeHdr", foreign_keys=[employee_id])
    role = relationship("RoleHdr")
    assigner = relationship("EmployeeHdr", foreign_keys=[assigned_by])