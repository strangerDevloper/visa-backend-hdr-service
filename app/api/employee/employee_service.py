# app/api/employee/employee_service.py (Services)
from sqlalchemy.orm import Session
from ... import models
from . import employee_types
from ...helpers import auth_utils
import uuid

def create_employee(db: Session, employee: employee_types.EmployeeCreate, created_by: int = None):
    db_employee = models.EmployeeHdr(**employee.dict())
    if created_by:
        db_employee.created_by = created_by
    db_employee.emp_uid = str(uuid.uuid4())
    default_password = auth_utils.generate_random_password()
    db_employee.password_hash = auth_utils.get_password_hash(default_password)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    db_employee.password = default_password #Return default password
    return db_employee

def get_employee(db: Session, employee_id: int):
    return db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()

def get_employee_by_uid(db: Session, emp_uid: str):
    return db.query(models.EmployeeHdr).filter(models.EmployeeHdr.emp_uid == emp_uid).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.EmployeeHdr).offset(skip).limit(limit).all()

def update_employee(db: Session, employee_id: int, employee_update: employee_types.EmployeeUpdate, modified_by: int = None):
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
    if db_employee:
        for key, value in employee_update.dict(exclude_unset=True).items():
            if key == "password":
                setattr(db_employee, "password_hash", auth_utils.get_password_hash(value))
            else:
                setattr(db_employee, key, value)
        if modified_by:
            db_employee.modified_by = modified_by
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int, modified_by: int = None):
    db_employee = db.query(models.EmployeeHdr).filter(models.EmployeeHdr.employee_id == employee_id).first()
    if db_employee:
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