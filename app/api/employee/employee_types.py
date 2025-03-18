# app/api/employee/employee_types.py (Schemas)
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic import validator


class EmployeeBase(BaseModel):
    employee_title: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    emergency_contact: Optional[str] = None
    marital_status: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    email: str
    mobile_no: str
    employee_code: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employee_title: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    emergency_contact: Optional[str] = None
    marital_status: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    email: Optional[str] = None
    mobile_no: Optional[str] = None
    employee_code: Optional[str] = None
    active_status: Optional[bool] = None
    is_absent: Optional[bool] = None
    absence_expiry: Optional[datetime] = None
    password: Optional[str] = None

    @validator("gender")
    def validate_gender(cls, value):
        if value is not None:
            value = value.upper()
            if value not in ["MALE", "FEMALE", "OTHER"]:
                raise ValueError("Gender must be one of: MALE, FEMALE, OTHER")
        return value

    @validator("marital_status")
    def validate_marital_status(cls, value):
        if value is not None:
            value = value.upper()
            if value not in ["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"]:
                raise ValueError("Marital status must be one of: SINGLE, MARRIED, DIVORCED, WIDOWED")
        return value

    @validator("id_proof_type")
    def validate_id_proof_type(cls, value):
        if value is not None:
            value = value.upper()
            if value not in ["AADHAR", "PAN", "VOTER_ID", "DRIVING_LICENSE", "PASSPORT", "OTHER"]:
                raise ValueError("ID proof type must be one of: AADHAR, PAN, VOTER_ID, DRIVING_LICENSE, PASSPORT, OTHER")
        return value


class Employee(EmployeeBase):
    employee_id: int
    emp_uid: str
    active_status: bool = True
    is_absent: bool = False
    absence_expiry: Optional[datetime] = None
    created_by: Optional[int] = None
    created_date: datetime
    modified_by: Optional[int] = None
    modified_date: Optional[datetime] = None
    password: Optional[str] = None  # Added password to return default password on creation.

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmployeeRoleCreate(BaseModel):
    role_id: int  # Only role_id is needed in the payload

class EmployeeRoleUpdate(BaseModel):
    role_id: int  # Only role_id is needed in the payload

class EmployeeRoleResponse(BaseModel):
    employee_role_id: int
    employee_id: int
    role_id: int
    assigned_at: datetime
    assigned_by: int

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

class EmployeeCountryAccessBase(BaseModel):
    country_ids: List[int]  # List of country IDs

class EmployeeCountryAccessCreate(EmployeeCountryAccessBase):
    pass

class EmployeeCountryAccessResponse(BaseModel):
    access_id: int
    employee_id: int
    country_id: int
    granted_at: datetime
    granted_by: int

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
