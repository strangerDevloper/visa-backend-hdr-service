# app/api/employee/employee_service.py
from sqlalchemy import func
from sqlalchemy.orm import Session # type: ignore
from ... import models
from ...models.employees import Gender, MaritalStatus, IDProofType
from . import employee_types
from ...helpers import auth_utils
import uuid
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def create_employee(db: Session, employee: employee_types.EmployeeCreate, created_by: int):
    """
    Create a new employee with validation for unique email and employee_code
    """
    # Check for existing email
    existing_email = db.query(models.EmployeeHdr).filter(
        func.lower(models.EmployeeHdr.email) == func.lower(employee.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An employee with this email already exists.",
        )

    # Check for existing employee_code
    existing_code = db.query(models.EmployeeHdr).filter(
        models.EmployeeHdr.employee_code == employee.employee_code
    ).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An employee with this employee code already exists.",
        )

    try:
        db_employee = models.EmployeeHdr(**employee.dict())
        db_employee.created_by = created_by
        db_employee.emp_uid = str(uuid.uuid4())
        default_password = auth_utils.generate_random_password()
        db_employee.password_hash = auth_utils.get_password_hash(default_password)
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        db_employee.password = default_password  # Only for the response
        return db_employee
    except IntegrityError as e:
        db.rollback()
        # This is a fallback in case our manual checks missed something
        if "employee_hdr_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee with this email already exists.",
            )
        elif "employee_hdr_employee_code_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee with this employee code already exists.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while creating the employee.",
        )
    
# def get_employee(db: Session, employee_id: int):
#     """
#     Get an employee by ID.
#     """
#     db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
#     if db_employee is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Employee with ID {employee_id} not found.",
#         )
#     return db_employee

def get_employee(db: Session, employee_id: int):
    """
    Get an employee by ID with their roles and country access information.
    """
    # Get the employee
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )
    
    # Get employee roles with role names
    roles = (
        db.query(
            models.EmployeeRole.role_id,
            models.RoleHdr.role_name
        )
        .join(models.RoleHdr, models.EmployeeRole.role_id == models.RoleHdr.role_id)
        .filter(models.EmployeeRole.employee_id == employee_id)
        .all()
    )
    
    # Get employee country access with country names
    country_access = (
        db.query(
            models.EmployeeVisaTypeAccess.country_id,
            models.CountryHdr.country_name
        )
        .join(models.CountryHdr, models.EmployeeVisaTypeAccess.country_id == models.CountryHdr.country_id)
        .filter(models.EmployeeVisaTypeAccess.employee_id == employee_id)
        .distinct()  # In case there are multiple entries for the same country
        .all()
    )
    
    # Convert the employee to dict and add the additional data
    employee_data = db_employee.__dict__
    employee_data['roles'] = [{'role_id': r.role_id, 'role_name': r.role_name} for r in roles]
    employee_data['country_access'] = [{'country_id': c.country_id, 'country_name': c.country_name} for c in country_access]
    
    return employee_data

def get_employee_by_uid(db: Session, emp_uid: str):
    """
    Get an employee by UID.
    """
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.emp_uid == emp_uid).first()
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with UID {emp_uid} not found.",
        )
    return db_employee

def get_employee_by_email(db: Session, email: str):
    """
    Get an employee by email.
    """
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.email == email).first()
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with email {email} not found.",
        )
    return db_employee

def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    country_id: Optional[int] = None,
    visa_process_id: Optional[int] = None,
    role_id: Optional[int] = None
) -> Tuple[List[models.EmployeeHdr], int]:
    """
    Get a list of employees with pagination and optional filtering by:
    - visa access (country_id and/or visa_process_id)
    - role assignment (role_id)
    """
    query = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.active_status == True)
    
    # We'll collect all subqueries for different filters
    subqueries = []
    
    # Filter by visa access if provided
    if country_id is not None or visa_process_id is not None:
        access_query = db.query(models.EmployeeVisaTypeAccess.employee_id)
        
        if country_id is not None:
            access_query = access_query.filter(
                models.EmployeeVisaTypeAccess.country_id == country_id
            )
        
        if visa_process_id is not None:
            access_query = access_query.filter(
                models.EmployeeVisaTypeAccess.visa_process_id == visa_process_id
            )
        
        subqueries.append(access_query.distinct())
    
    # Filter by role if provided
    if role_id is not None:
        role_query = db.query(models.EmployeeRole.employee_id).filter(
            models.EmployeeRole.role_id == role_id
        )
        subqueries.append(role_query.distinct())
    
    # Apply all filters if any exist
    if subqueries:
        # Start with the first subquery
        combined_query = subqueries[0]
        
        # Intersect with additional subqueries (AND condition)
        for subq in subqueries[1:]:
            combined_query = combined_query.intersect(subq)
        
        employee_ids = combined_query.subquery()
        query = query.join(
            employee_ids,
            models.EmployeeHdr.employee_id == employee_ids.c.employee_id
        )
    
    total_count = query.count()
    employees = query.offset(skip).limit(limit).all()
    return employees, total_count

def update_employee(db: Session, employee_id: int, employee_update: employee_types.EmployeeUpdate, modified_by: int = None):
    """
    Update an existing employee.
    """
    try:
        db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
        if db_employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {employee_id} not found.",
            )

        update_data = employee_update.dict(exclude_unset=True)

        # Convert string values to Enum values
        if "gender" in update_data and update_data["gender"] is not None:
            try:
                update_data["gender"] = Gender[update_data["gender"].upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid gender value: {update_data['gender']}. Valid values are: MALE, FEMALE, OTHER.",
                )
        if "marital_status" in update_data and update_data["marital_status"] is not None:
            try:
                update_data["marital_status"] = MaritalStatus[update_data["marital_status"].upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid marital status value: {update_data['marital_status']}. Valid values are: SINGLE, MARRIED, DIVORCED, WIDOWED.",
                )
        if "id_proof_type" in update_data and update_data["id_proof_type"] is not None:
            try:
                update_data["id_proof_type"] = IDProofType[update_data["id_proof_type"].upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid ID proof type value: {update_data['id_proof_type']}. Valid values are: AADHAR, PAN, VOTER_ID, DRIVING_LICENSE, PASSPORT, OTHER.",
                )

        # Update the employee fields
        for key, value in update_data.items():
            if key == "password":
                setattr(db_employee, "password_hash", auth_utils.get_password_hash(value))
            else:
                setattr(db_employee, key, value)

        if modified_by:
            db_employee.modified_by = modified_by

        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError as e:
        db.rollback()
        if "employee_hdr_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee with this email already exists.",
            )
        elif "employee_hdr_mobile_no_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee with this mobile number already exists.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred while updating the employee.",
            )

def delete_employee(db: Session, employee_id: int, modified_by: int = None):
    """
    Soft delete an employee by setting active_status to False.
    """
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )
    db_employee.active_status = False
    if modified_by:
        db_employee.modified_by = modified_by
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_login_info(db: Session, employee_id: int):
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
    if db_employee:
        db_employee.last_login = datetime.utcnow()
        db_employee.login_count += 1
        db.commit()
        db.refresh(db_employee)
    return db_employee

def assign_role_to_employee(db: Session, employee_id: int, role_id: int, assigned_by: int):
    """
    Assign a role to an employee.
    """
    try:
        db_employee_role = models.EmployeeRole(
            employee_id=employee_id,
            role_id=role_id,
            assigned_by=assigned_by,
        )
        db.add(db_employee_role)
        db.commit()
        db.refresh(db_employee_role)
        return db_employee_role
    except IntegrityError as e:
        db.rollback()  # Rollback the transaction to avoid leaving the database in an inconsistent state
        if "employee_role_employee_id_fkey" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {employee_id} does not exist.",
            )
        elif "employee_role_role_id_fkey" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} does not exist.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred while assigning the role.",
            )

def update_employee_role(db: Session, employee_role_id: int, role_id: int, assigned_by: int):
    """
    Update an existing role assignment for an employee.
    """
    try:
        db_employee_role = db.query(models.EmployeeRole).filter(models.EmployeeRole.employee_role_id == employee_role_id).first()
        if db_employee_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role assignment with ID {employee_role_id} not found.",
            )
        db_employee_role.role_id = role_id
        db_employee_role.assigned_by = assigned_by
        db.commit()
        db.refresh(db_employee_role)
        return db_employee_role
    except IntegrityError as e:
        db.rollback()  # Rollback the transaction to avoid leaving the database in an inconsistent state
        if "employee_role_role_id_fkey" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} does not exist.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An error occurred while updating the role assignment.",
            )

def get_employee_role(db: Session, employee_role_id: int):
    """
    Get a specific role assignment by ID.
    """
    db_employee_role = db.query(models.EmployeeRole).filter(models.EmployeeRole.employee_role_id == employee_role_id).first()
    if db_employee_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role assignment with ID {employee_role_id} not found.",
        )
    return db_employee_role

def get_roles_for_employee(db: Session, employee_id: int):
    """
    Get all role assignments for a specific employee.
    """
    return db.query(models.EmployeeRole).filter(models.EmployeeRole.employee_id == employee_id).all()

def assign_country_access(db: Session, employee_id: int, country_ids: List[int], granted_by: int):
    """
    Assign access to multiple countries for an employee.
    """
    try:
        for country_id in country_ids:
            db_access = models.EmployeeVisaTypeAccess(
                employee_id=employee_id,
                country_id=country_id,
                granted_by=granted_by,
            )
            db.add(db_access)
        db.commit()
        return db.query(models.EmployeeVisaTypeAccess).filter(models.EmployeeVisaTypeAccess.employee_id == employee_id).all()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while assigning country access: {str(e)}",
        )

def remove_country_access(db: Session, employee_id: int, country_ids: List[int]):
    """
    Remove access for multiple countries for an employee.
    """
    try:
        db.query(models.EmployeeVisaTypeAccess).filter(
            models.EmployeeVisaTypeAccess.employee_id == employee_id,
            models.EmployeeVisaTypeAccess.country_id.in_(country_ids),
        ).delete(synchronize_session=False)
        db.commit()
        return {"message": "Country access removed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while removing country access: {str(e)}",
        )

def get_country_access_for_employee(db: Session, employee_id: int):
    """
    Get all country access records for an employee.
    """
    db_accesses = db.query(models.EmployeeVisaTypeAccess).filter(models.EmployeeVisaTypeAccess.employee_id == employee_id).all()
    if not db_accesses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No country access records found for employee with ID {employee_id}",
        )
    return db_accesses