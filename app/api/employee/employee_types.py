# app/api/employee/employee_types.py (Schemas)
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic import validator
from enum import Enum

# Define enums for the constrained values
class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class MaritalStatusEnum(str, Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"

class IdProofTypeEnum(str, Enum):
    AADHAR = "AADHAR"
    PAN = "PAN"
    VOTER_ID = "VOTER_ID"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    PASSPORT = "PASSPORT"
    OTHER = "OTHER"

def validate_gender(cls, value):
    if value is not None:
        value = value.upper()
        if value not in [gender.value for gender in GenderEnum]:
            raise ValueError(f"Gender must be one of: {', '.join([gender.value for gender in GenderEnum])}")
    return value

def validate_marital_status(cls, value):
    if value is not None:
        value = value.upper()
        if value not in [status.value for status in MaritalStatusEnum]:
            raise ValueError(f"Marital status must be one of: {', '.join([status.value for status in MaritalStatusEnum])}")
    return value

def validate_id_proof_type(cls, value):
    if value is not None:
        value = value.upper()
        if value not in [proof.value for proof in IdProofTypeEnum]:
            raise ValueError(f"ID proof type must be one of: {', '.join([proof.value for proof in IdProofTypeEnum])}")
    return value

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

    # Assign the validator functions
    _validate_gender = validator("gender", allow_reuse=True)(validate_gender)
    _validate_marital_status = validator("marital_status", allow_reuse=True)(validate_marital_status)
    _validate_id_proof_type = validator("id_proof_type", allow_reuse=True)(validate_id_proof_type)

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

    # Reuse the same validator functions
    _validate_gender = validator("gender", allow_reuse=True)(validate_gender)
    _validate_marital_status = validator("marital_status", allow_reuse=True)(validate_marital_status)
    _validate_id_proof_type = validator("id_proof_type", allow_reuse=True)(validate_id_proof_type)

class EmployeeRoleResponse(BaseModel):
    role_id: int
    role_name: str

    class Config:
        from_attributes = True

class EmployeeCountryAccessResponse(BaseModel):
    country_id: int
    country_name: str

    class Config:
        from_attributes = True


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
    password: Optional[str] = None
    roles: List[EmployeeRoleResponse] = []  # List of roles
    country_access: List[EmployeeCountryAccessResponse] = []  # List of country access

    class Config:
        from_attributes = True

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
