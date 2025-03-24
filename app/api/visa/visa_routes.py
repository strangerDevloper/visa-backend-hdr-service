# app/api/visa/visa_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union

from ...config.database import get_db
from . import visa_types, visa_service
from ...api.dependencies import CurrentEmployee

router = APIRouter(prefix="/visa", tags=["visa"])

@router.post("/", response_model=visa_types.VisaProcess, status_code=status.HTTP_201_CREATED)
def create_visa_process(
    visa_process: visa_types.VisaProcessCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Creates a new visa process."""
    return visa_service.create_visa_process(db, visa_process, current_employee.employee_id)

@router.get("/{visa_process_id}", response_model=visa_types.VisaProcess)
def get_visa_process(
    visa_process_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Retrieves a visa process by its ID."""
    db_visa_process = visa_service.get_visa_process(db, visa_process_id)
    if not db_visa_process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa process not found")
    return db_visa_process

@router.get("/", response_model=Dict[str, Union[List[visa_types.VisaProcess], int]])
def get_all_visa_processes(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
    country_id: Optional[int] = Query(None, description="Filter by country ID"),
    process_name: Optional[str] = Query(None, description="Filter by process name"),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
):
    """Retrieves all visa processes with optional filters."""
    visa_processes, total_count = visa_service.get_all_visa_processes(
        db, country_id=country_id, process_name=process_name, skip=skip, limit=limit
    )
    return {"visa_processes": visa_processes, "total_count": total_count}

@router.put("/{visa_process_id}", response_model=visa_types.VisaProcess)
def update_visa_process(
    visa_process_id: int,
    visa_process_update: visa_types.VisaProcessUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Updates an existing visa process."""
    db_visa_process = visa_service.update_visa_process(db, visa_process_id, visa_process_update, current_employee.employee_id)
    if not db_visa_process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa process not found")
    return db_visa_process

@router.delete("/{visa_process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_visa_process(
    visa_process_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Deactivates a visa process."""
    if not visa_service.deactivate_visa_process(db, visa_process_id, current_employee.employee_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visa process not found")
    return

@router.post("/{visa_process_id}/rate-cuts", response_model=visa_types.VisaRateCutCreate, status_code=status.HTTP_201_CREATED)
def create_rate_cut(
    visa_process_id: int,
    rate_cut: visa_types.VisaRateCutCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Creates a new rate cut for a visa process."""
    db_rate_cut = visa_service.create_rate_cut(db, visa_process_id, rate_cut, current_employee.employee_id)
    return db_rate_cut

@router.put("/rate-cuts/{rate_cut_id}", response_model=visa_types.VisaRateCutCreate)
def update_rate_cut(
    rate_cut_id: int,
    rate_cut_update: visa_types.VisaRateCutUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Updates an existing rate cut."""
    db_rate_cut = visa_service.update_rate_cut(db, rate_cut_id, rate_cut_update, current_employee.employee_id)
    if not db_rate_cut:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate cut not found")
    return db_rate_cut

@router.get("/{visa_process_id}/fields", response_model=List[visa_types.VisaFieldCreate])
def get_all_fields(
    visa_process_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Retrieves all fields for a visa process."""
    return visa_service.get_all_fields(db, visa_process_id)

@router.put("/fields/{field_id}", response_model=visa_types.VisaFieldCreate)
def update_field(
    field_id: int,
    field_update: visa_types.VisaFieldUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Updates an existing field in a visa process."""
    db_field = visa_service.update_field(db, field_id, field_update, current_employee.employee_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return db_field