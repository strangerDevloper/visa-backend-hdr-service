# app/api/employee/employee_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database import get_db
from . import employee_types, employee_service
from ...helpers import auth_utils
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ...api.dependencies import CurrentEmployee
from ... import models
from typing import List, Dict, Union


router = APIRouter(prefix="/employees", tags=["employees"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/employees/signin") # type: ignore

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
def read_employees(current_employee: CurrentEmployee, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees, total_count = employee_service.get_employees(db, skip=skip, limit=limit)
    return {"employees": employees, "total_count": total_count}


@router.put("/{employee_id}", response_model=employee_types.Employee)
def update_employee(employee_id: int, employee_update: employee_types.EmployeeUpdate, current_employee: CurrentEmployee , db: Session = Depends(get_db)):
    db_employee = employee_service.update_employee(db, employee_id, employee_update, current_employee.employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, current_employee: CurrentEmployee, db: Session = Depends(get_db)):
    employee_service.delete_employee(db, employee_id, current_employee.employee_id)
    return

@router.post("/signin", response_model=employee_types.Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_employee = employee_service.get_employee_by_email(db, form_data.username) # Use email
    print("db employee" , db_employee)
    if not db_employee or not auth_utils.verify_password(form_data.password, db_employee.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password") #Updated error message
    access_token = auth_utils.create_access_token(data={"sub": str(db_employee.employee_id)})
    employee_service.update_login_info(db, db_employee.employee_id)
    return employee_types.Token(access_token=access_token)