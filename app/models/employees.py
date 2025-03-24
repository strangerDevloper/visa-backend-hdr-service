# app/models/employees.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..config.database import Base
import enum

class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class MaritalStatus(enum.Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"

class IDProofType(enum.Enum):
    AADHAR = "AADHAR"
    PAN = "PAN"
    VOTER_ID = "VOTER_ID"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    PASSPORT = "PASSPORT"
    OTHER = "OTHER"
    

class EmployeeHdr(Base):
    __tablename__ = "employee_hdr"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_title = Column(String(50))
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    gender = Column(Enum(Gender))  # Use the Gender enum
    dob = Column(DateTime)
    emergency_contact = Column(String(20))
    marital_status = Column(Enum(MaritalStatus))  # Use the MaritalStatus enum
    id_proof_type = Column(Enum(IDProofType))  # Use the IDProofType enum
    id_number = Column(String(50))
    address = Column(String)
    pincode = Column(String(10))
    email = Column(String)
    mobile_no = Column(String)
    employee_code = Column(String)
    emp_uid = Column(String)
    active_status = Column(Boolean, default=True)
    is_absent = Column(Boolean, default=False)
    absence_expiry = Column(DateTime, nullable=True)
    password_hash = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    created_date = Column(DateTime, server_default=func.now())
    modified_by = Column(Integer, ForeignKey('employee_hdr.employee_id'))
    modified_date = Column(DateTime, onupdate=func.now())

    creator = relationship('EmployeeHdr', remote_side=[employee_id], foreign_keys=[created_by])
    modifier = relationship('EmployeeHdr', remote_side=[employee_id], foreign_keys=[modified_by])