# app/services/role_service.py
from typing import List
from sqlalchemy.orm import Session
from app.api.role.role_types import PermissionBase
from app.models import RoleHdr, RolePermissions, Permissions
from fastapi import HTTPException, status

def create_role(db: Session, role_data: dict, permission_ids: List[int], created_by: int):
    # Check if role name already exists
    existing_role = db.query(RoleHdr).filter(RoleHdr.role_name == role_data.get("role_name")).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    # Create new role
    new_role = RoleHdr(**role_data, created_by=created_by)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # Add permissions
    add_permissions_to_role(db, new_role.role_id, permission_ids, created_by)
    return new_role

def get_role(db: Session, role_id: int):
    role = db.query(RoleHdr).filter(RoleHdr.role_id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

def get_all_roles(db: Session):
    return db.query(RoleHdr).all()

def update_role(db: Session, role_id: int, update_data: dict, modified_by: int):
    role = get_role(db, role_id)
    for key, value in update_data.items():
        setattr(role, key, value)
    role.modified_by = modified_by
    db.commit()
    db.refresh(role)
    return role

def delete_role(db: Session, role_id: int):
    role = get_role(db, role_id)
    
    # Delete associated permissions first
    db.query(RolePermissions).filter(RolePermissions.role_id == role_id).delete()
    
    db.delete(role)
    db.commit()
    return {"message": "Role deleted successfully"}

def add_permissions_to_role(db: Session, role_id: int, permission_ids: List[int], modified_by: int):
    role = get_role(db, role_id)
    
    # Verify permissions exist
    existing_permissions = db.query(Permissions).filter(Permissions.permission_id.in_(permission_ids)).all()
    if len(existing_permissions) != len(permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more invalid permission IDs"
        )
    
    # Remove existing permissions
    db.query(RolePermissions).filter(RolePermissions.role_id == role_id).delete()
    
    # Add new permissions
    for perm_id in permission_ids:
        role_permission = RolePermissions(
            role_id=role_id,
            permission_id=perm_id,
        )
        db.add(role_permission)
    
    # Update role modified info
    role.modified_by = modified_by
    db.commit()
    return role

def get_role_with_permissions(db: Session, role_id: int):
    # Get role with all fields
    role = db.query(RoleHdr).filter(RoleHdr.role_id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Get permissions and convert to Pydantic models
    permissions = (
        db.query(Permissions)
        .join(RolePermissions, Permissions.permission_id == RolePermissions.permission_id)
        .filter(RolePermissions.role_id == role_id)
        .all()
    )
    
    # Convert permissions to PermissionBase models
    permission_bases = [PermissionBase.from_orm(p) for p in permissions]
    
    return role, permission_bases

def get_all_permissions(db: Session):
    """
    Fetch all permissions from the database.
    """
    try:
        permissions = db.query(Permissions).all()
        return permissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching permissions: {str(e)}"
        )