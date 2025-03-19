# app/api/common/common_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import List, Optional
from app.api.common.common_types import EmployeeResponse, PermissionResponse, RoleResponse, UserResponse
from app.models import User, EmployeeHdr, EmployeeRole, RoleHdr, RolePermissions, Permissions
from app.core.constants import USER_TYPE_EMPLOYEE, USER_TYPE_USER

def get_user_response(user: User) -> UserResponse:
    """
    Builds a UserResponse object from a User model instance.
    """
    return UserResponse(
        user_type=USER_TYPE_USER,
        user_id=user.user_id,
        name=user.name,
        username=user.username,
        email=user.email,
    )

def get_employee_response(employee: EmployeeHdr, db: Session) -> EmployeeResponse:
    """
    Builds an EmployeeResponse object from an EmployeeHdr model instance.
    Fetches all roles and permissions associated with the employee.
    """
    # Fetch all roles associated with the employee
    employee_roles = (
        db.query(EmployeeRole)
        .options(
            joinedload(EmployeeRole.role).joinedload(RoleHdr.role_permissions).joinedload(RolePermissions.permission)
        )
        .filter(EmployeeRole.employee_id == employee.employee_id)
        .all()
    )

    if not employee_roles:
        raise HTTPException(status_code=404, detail="No roles found for the employee")
    # Extract roles and permissions
    roles = []
    for employee_role in employee_roles:
        role = employee_role.role
        permissions = [
            PermissionResponse(
                permission_id=rp.permission.permission_id,
                permission_name=rp.permission.permission_name,
                description=rp.permission.description,
                resource=rp.permission.resource,
                action=rp.permission.action.value,  # Convert Enum to string
                method=rp.permission.method.value,  # Convert Enum to string
            )
            for rp in role.role_permissions
        ]
        roles.append(
            RoleResponse(
                role_id=role.role_id,
                role_name=role.role_name,
                role_description=role.role_description,
                is_system_role=role.is_system_role,
                permissions=permissions,
            )
        )

    return EmployeeResponse(
        user_type=USER_TYPE_EMPLOYEE,
        user_id=employee.employee_id,
        name=f"{employee.first_name} {employee.last_name}",
        username=employee.employee_code,
        email=employee.email,
        roles=roles,  # List of roles
    )