# app/models/employee_country_access.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class EmployeeCountryAccess(Base):
    __tablename__ = "employee_country_access"

    country_access_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)
    country_id = Column(Integer, ForeignKey('country_hdr.country_id'), nullable=False)
    granted_at = Column(DateTime, server_default=func.now())
    granted_by = Column(Integer, ForeignKey('employee_hdr.employee_id'), nullable=False)

    # Relationships
    employee = relationship("EmployeeHdr", foreign_keys=[employee_id])
    country = relationship("CountryHdr")
    granted_by_employee = relationship("EmployeeHdr", foreign_keys=[granted_by], remote_side="employee_hdr.employee_id")

    def __repr__(self):
        return f"<EmployeeCountryAccess(country_access_id={self.country_access_id}, employee_id={self.employee_id}, country_id={self.country_id}, granted_at='{self.granted_at}', granted_by={self.granted_by})>"