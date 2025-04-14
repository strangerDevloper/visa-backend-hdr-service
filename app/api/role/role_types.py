# app/schemas/role_types.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PermissionBase(BaseModel):
    permission_id: int
    permission_name: str
    description: Optional[str]
    resource: str
    action: str
    method: str

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    role_name: str
    role_description: Optional[str] = None
    is_system_role: bool = False
    permission_ids: List[int]

class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    role_description: Optional[str] = None
    is_system_role: Optional[bool] = None

class RolePermissionsUpdate(BaseModel):
    permission_ids: List[int]

class RoleResponse(BaseModel):
    role_id: int
    role_name: str
    role_description: Optional[str]
    is_system_role: bool
    created_by: Optional[int]
    created_date: Optional[datetime]
    modified_by: Optional[int]
    modified_date: Optional[datetime]
    permissions: Optional[List[PermissionBase]] = None

    class Config:
        from_attributes = True

class PermissionResponse(BaseModel):
    permission_id: int
    permission_name: str
    description: Optional[str]
    resource: str
    action: str
    method: str

    class Config:
        from_attributes = True