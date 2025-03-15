# app/api/country/country_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ...database import get_db
from . import country_types, country_service
from ...api.dependencies import CurrentEmployee
from typing import List, Dict, Union, Any

router = APIRouter(prefix="/countries", tags=["countries"])

@router.post("/", response_model=country_types.Country, status_code=status.HTTP_201_CREATED)
def create_country(
    country: country_types.CountryCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Creates a new country."""
    db_country_name_exists = country_service.get_country_by_name(db, country.country_name)
    if db_country_name_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Country name already exists"
        )

    db_country_code_exists = country_service.get_country_by_code(db, country.country_code)
    if db_country_code_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Country code already exists"
        )

    return country_service.create_country(db, country, current_employee.employee_id)

@router.get("/{country_id}", response_model=country_types.Country)
def get_country(
    country_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Retrieves a country by its ID."""
    db_country = country_service.get_country(db, country_id)
    if not db_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return db_country

@router.get("/", response_model=Dict[str, Union[List[country_types.Country], int]])
def get_countries(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
    is_active: Union[bool, None] = Query(
        None, description="Filter by active status (true/false)"
    ),
):
    """Retrieves a list of countries with pagination, optional filtering, and returns total count."""
    countries, total_count = country_service.get_countries_paginated(
        db, skip=skip, limit=limit, is_active=is_active
    )
    return {"countries": countries, "total_count": total_count}

@router.put("/{country_id}", response_model=country_types.Country)
def update_country(
    country_id: int,
    country_update: country_types.CountryUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Updates an existing country."""
    db_country = country_service.get_country(db, country_id)
    if not db_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country_service.update_country(db, country_id, country_update, current_employee.employee_id)

@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    country_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Deactivates a country."""
    db_country = country_service.get_country(db, country_id)
    if not db_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    country_service.deactivate_country(db, country_id, current_employee.employee_id)
    return