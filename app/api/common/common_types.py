# app/api/common/common_types.py

from pydantic import BaseModel, Field
from typing import Union
from app.models.users import User  # Import your SQLAlchemy User model
from app.models.employees import EmployeeHdr  # Import your SQLAlchemy EmployeeHdr model (if applicable)

# Base response model
class BaseUserResponse(BaseModel):
    user_type: str = Field(..., description="Type of the user (USER or EMPLOYEE)")

# User-specific response model
class UserResponse(BaseUserResponse):
    user_id: int
    username: str
    email: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

# Employee-specific response model
class EmployeeResponse(BaseUserResponse):
    employee_id: int
    employee_name: str
    email: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

# Union of possible responses
UserOrEmployeeResponse = Union[UserResponse, EmployeeResponse]