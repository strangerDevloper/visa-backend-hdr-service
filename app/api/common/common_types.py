# app/api/common/common_types.py

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

from app.core.constants import USER_TYPE_EMPLOYEE, UserType

# Permission response model
class PermissionResponse(BaseModel):
    permission_id: int
    permission_name: str
    description: Optional[str]
    resource: str
    action: str
    method: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

# Role response model
class RoleResponse(BaseModel):
    role_id: int
    role_name: str
    role_description: Optional[str]
    is_system_role: bool
    permissions: List[PermissionResponse]  # List of permissions associated with the role

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

# Base response model
class BaseUserResponse(BaseModel):
    user_type: str = Field(..., description="Type of the user (USER or EMPLOYEE or VENDOR)")

# User-specific response model
class UserResponse(BaseUserResponse):
    user_id: int
    name: str
    username: str
    email: str
    contact_number: str
    address: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class VendorResponse(BaseUserResponse):
    user_id: int
    email: str
    name: str
    username: str
    vendor_code: str
    contact_number: str
    address: str
    status: str


# Employee response model
class EmployeeResponse(BaseUserResponse):
    user_id: int
    name: str
    username: str
    email: str
    contact_number: str
    address: str
    roles: List[RoleResponse]  # List of roles associated with the employee

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
# Union of possible responses
UserOrEmployeeResponse = Union[UserResponse, EmployeeResponse]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SignInRequest(BaseModel):
    username: str
    password: str
    user_type: UserType = USER_TYPE_EMPLOYEE  # Default to "employee"