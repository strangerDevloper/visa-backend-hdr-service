# app/api/roles/role_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.common.common_types import PermissionResponse
from app.api.dependencies import CurrentEmployee, CurrentUser
from app.config.database import get_db
from app.api.role.role_types import PermissionBase, RoleCreate, RoleResponse, RoleUpdate, RolePermissionsUpdate
from app.api.role.role_service import (
    create_role,
    get_all_permissions,
    get_all_roles,
    get_role_with_permissions,
    update_role,
    delete_role,
    add_permissions_to_role
)

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_new_role(
    role_data: RoleCreate,
    current_employee: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        # Create the role
        new_role = create_role(
            db=db,
            role_data=role_data.dict(exclude={"permission_ids"}),
            permission_ids=role_data.permission_ids,
            created_by=current_employee.employee_id
        )
        
        # Get the role with permissions
        role, permissions = get_role_with_permissions(db, new_role.role_id)
        
        # Construct the response
        response = RoleResponse(
            role_id=role.role_id,
            role_name=role.role_name,
            role_description=role.role_description,
            is_system_role=role.is_system_role,
            created_by=role.created_by,
            created_date=role.created_date,
            modified_by=role.modified_by,
            modified_date=role.modified_date,
            permissions=permissions  # Now properly formatted as PermissionBase instances
        )
        
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[RoleResponse])
def get_all_roles_api(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    try:
        roles = get_all_roles(db)
        return [
            RoleResponse(
                **role.__dict__,
                permissions=[
                    PermissionBase(**perm.__dict__) 
                    for perm in get_role_with_permissions(db, role.role_id)[1]
                ]
            ) 
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/permissions", response_model=List[PermissionResponse])
def get_all_permissions_api(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Fetch all permissions available in the system.
    """
    try:
        permissions = get_all_permissions(db)
        return [
            PermissionResponse(
                permission_id=perm.permission_id,
                permission_name=perm.permission_name,
                description=perm.description,
                resource=perm.resource,
                action=perm.action.value,  # Convert Enum to string
                method=perm.method.value,  # Convert Enum to string
            )
            for perm in permissions
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching permissions: {str(e)}"
        )

@router.get("/{role_id}", response_model=RoleResponse)
def get_single_role(
    role_id: int, 
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    try:
        role, permissions = get_role_with_permissions(db, role_id)
        return RoleResponse(
            **role.__dict__,
            permissions=[PermissionBase(**perm.__dict__) for perm in permissions]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{role_id}", response_model=RoleResponse)
def update_role_api(
    role_id: int,
    role_data: RoleUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    try:
        updated_role = update_role(
            db=db,
            role_id=role_id,
            update_data=role_data.dict(exclude_unset=True),
            modified_by=current_employee.employee_id
        )
        role, permissions = get_role_with_permissions(db, role_id)
        return RoleResponse(
            **role.__dict__,
            permissions=[PermissionBase(**perm.__dict__) for perm in permissions]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{role_id}/permission", response_model=RoleResponse)
def update_role_permissions(
    role_id: int,
    permissions_data: RolePermissionsUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    try:
        updated_role = add_permissions_to_role(
            db=db,
            role_id=role_id,
            permission_ids=permissions_data.permission_ids,
            modified_by=current_employee.employee_id
        )
        role, permissions = get_role_with_permissions(db, role_id)
        return RoleResponse(
            **role.__dict__,
            permissions=[PermissionBase(**perm.__dict__) for perm in permissions]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
def delete_role_api(
    role_id: int, 
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    try:
        delete_role(db, role_id)
        return {"message": "Role deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )