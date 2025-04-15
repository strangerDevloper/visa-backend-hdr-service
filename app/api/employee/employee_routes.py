# app/api/employee/employee_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import USER_TYPE_EMPLOYEE
from ...config.database import get_db
from . import employee_types, employee_service
from ...helpers import auth_utils
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ...api.dependencies import CurrentEmployee
from ... import models
from typing import List, Dict, Optional, Union


router = APIRouter(prefix="/employees", tags=["employees"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/employees/signin") # type: ignore

@router.post("/", response_model=employee_types.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: employee_types.EmployeeCreate, current_employee: CurrentEmployee, db: Session = Depends(get_db)):
    return employee_service.create_employee(db, employee, current_employee.employee_id)

@router.get("/{employee_id}", response_model=employee_types.Employee)
def read_employee(employee_id: int, current_employee: CurrentEmployee, db: Session = Depends(get_db)):
    db_employee = employee_service.get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.get("/", response_model=Dict[str, Union[List[employee_types.Employee], int]])
def read_employees(
    current_employee: CurrentEmployee,
    skip: int = 0,
    limit: int = 100,
    country_id: Optional[int] = None,
    visa_process_id: Optional[int] = None,
    role_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    employees, total_count = employee_service.get_employees(
        db,
        skip=skip,
        limit=limit,
        country_id=country_id,
        visa_process_id=visa_process_id,
        role_id=role_id
    )
    return {"employees": employees, "total_count": total_count}

@router.put("/{employee_id}", response_model=employee_types.Employee)
def update_employee(employee_id: int, employee_update: employee_types.EmployeeUpdate, current_employee: CurrentEmployee, db: Session = Depends(get_db)):
    db_employee = employee_service.update_employee(db, employee_id, employee_update, current_employee.employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(employee_id: int, current_employee: CurrentEmployee, db: Session = Depends(get_db)):
    employee_service.delete_employee(db, employee_id, current_employee.employee_id)
    return {"message": "Employee deleted successfully"}

@router.post("/{employee_id}/roles", response_model=employee_types.EmployeeRoleResponse, status_code=status.HTTP_201_CREATED)
def assign_role_to_employee(
    employee_id: int,
    employee_role: employee_types.EmployeeRoleCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Assign a role to an employee.
    """
    return employee_service.assign_role_to_employee(db, employee_id, employee_role.role_id, current_employee.employee_id)

@router.put("/{employee_id}/roles/{employee_role_id}", response_model=employee_types.EmployeeRoleResponse)
def update_employee_role(
    employee_id: int,
    employee_role_id: int,
    employee_role_update: employee_types.EmployeeRoleUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Update an existing role assignment for an employee.
    """
    db_employee_role = employee_service.update_employee_role(db, employee_role_id, employee_role_update.role_id, current_employee.employee_id)
    if db_employee_role is None:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return db_employee_role

@router.get("/{employee_id}/roles", response_model=list[employee_types.EmployeeRoleResponse])
def get_roles_for_employee(
    employee_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Get all role assignments for a specific employee.
    """
    return employee_service.get_roles_for_employee(db, employee_id)

@router.get("/{employee_id}/roles/{employee_role_id}", response_model=employee_types.EmployeeRoleResponse)
def get_employee_role(
    employee_id: int,
    employee_role_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Get a specific role assignment by ID.
    """
    db_employee_role = employee_service.get_employee_role(db, employee_role_id)
    if db_employee_role is None:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return db_employee_role


@router.get("/roles/{employee_role_id}", response_model=employee_types.EmployeeRoleResponse)
def get_employee_role(
    employee_role_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Get a specific role assignment by ID.
    """
    db_employee_role = employee_service.get_employee_role(db, employee_role_id)
    if db_employee_role is None:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return db_employee_role

@router.post("/{employee_id}/country-access", response_model=list[employee_types.EmployeeCountryAccessResponse], status_code=status.HTTP_201_CREATED)
def assign_country_access_to_employee(
    employee_id: int,
    access: employee_types.EmployeeCountryAccessCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Assign access to multiple countries for an employee.
    """
    return employee_service.assign_country_access(
        db,
        employee_id=employee_id,
        country_ids=access.country_ids,
        granted_by=current_employee.employee_id,
    )

@router.delete("/{employee_id}/country-access", response_model=dict)
def remove_country_access_from_employee(
    employee_id: int,
    remove: employee_types.EmployeeCountryAccessCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Remove access for multiple countries for an employee.
    """
    return employee_service.remove_country_access(
        db,
        employee_id=employee_id,
        country_ids=remove.country_ids,
    )

@router.get("/{employee_id}/country-access", response_model=list[employee_types.EmployeeCountryAccessResponse])
def get_country_access_for_employee(
    employee_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Get all country access records for a specific employee.
    """
    return employee_service.get_country_access_for_employee(
        db,
        employee_id=employee_id,
    )

@router.post("/signin", response_model=employee_types.Token)
def signin_employee(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_employee = employee_service.get_employee_by_email(db, form_data.username)
    if not db_employee or not auth_utils.verify_password(form_data.password, db_employee.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user_id = db_employee.employee_id
    user_type = USER_TYPE_EMPLOYEE

    access_token = auth_utils.create_access_token(data={"sub": str(user_id)}, user_type=user_type)
    employee_service.update_login_info(db, db_employee.employee_id)
    return employee_types.Token(access_token=access_token)