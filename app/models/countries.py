# app/models/countries.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class CountryHdr(Base):
    __tablename__ = "country_hdr"

    country_id = Column(Integer, primary_key=True, autoincrement=True)
    country_name = Column(String(150), nullable=False)
    country_code = Column(String(50), nullable=False)
    currency = Column(String(50), nullable=True)
    official_language  = Column(String(100), nullable=True)
    description  = Column(String(), nullable=True)
    is_active = Column(Boolean, default=True)
    logo_path = Column(String)
    created_date = Column(DateTime, server_default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id')) # Updated FK
    modified_employee = relationship("EmployeeHdr") # Updated relationship

    # Relationship to media
    media = relationship("CountryServiceMedia", back_populates="country")
