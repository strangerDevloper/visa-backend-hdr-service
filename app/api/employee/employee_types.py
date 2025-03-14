# app/api/employee/employee_types.py (Schemas)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    employee_name: str
    email: str
    mobile_no: str
    employee_code: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employee_name: Optional[str] = None
    email: Optional[str] = None
    mobile_no: Optional[str] = None
    employee_code: Optional[str] = None
    active_status: Optional[bool] = None
    is_absent: Optional[bool] = None
    absence_expiry: Optional[datetime] = None
    password: Optional[str] = None # Added password for update

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
    password: Optional[str] = None #Added password to return default password on creation.

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"