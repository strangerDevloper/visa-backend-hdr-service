# app/api/country/country_service.py
from sqlalchemy.orm import Session
from ... import models
from . import country_types
from typing import Union

def get_country_by_name(db: Session, country_name: str):
    """Retrieves a country by its name."""
    return db.query(models.CountryHdr).filter(models.CountryHdr.country_name == country_name).first()

def get_country_by_code(db: Session, country_code: str):
    """Retrieves a country by its code."""
    return db.query(models.CountryHdr).filter(models.CountryHdr.country_code == country_code).first()

def create_country(db: Session, country: country_types.CountryCreate, modified_by: int):
    """Creates a new country."""
    db_country = models.CountryHdr(
        country_name=country.country_name,
        country_code=country.country_code,
        logo_path=country.logo_path,
        modified_by=modified_by,
    )
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

def get_country(db: Session, country_id: int):
    """Retrieves a country by its ID."""
    return db.query(models.CountryHdr).filter(models.CountryHdr.country_id == country_id).first()

def get_countries(db: Session, skip: int = 0, limit: int = 10, is_active: bool = None):
    """Retrieves a list of countries with pagination and optional filtering by active status."""
    query = db.query(models.CountryHdr)
    if is_active is not None:
        query = query.filter(models.CountryHdr.is_active == is_active)
    return query.offset(skip).limit(limit).all()

def get_countries_paginated(db: Session, skip: int = 0, limit: int = 10, is_active: Union[bool, None] = None):
    """Retrieves a list of countries with pagination, optional filtering, and returns total count."""
    query = db.query(models.CountryHdr)
    if is_active is not None:
        query = query.filter(models.CountryHdr.is_active == is_active)

    total_count = query.count()
    countries = query.offset(skip).limit(limit).all()
    return countries, total_count

def update_country(db: Session, country_id: int, country_update: country_types.CountryUpdate, modified_by: int):
    """Updates an existing country."""
    db_country = db.query(models.CountryHdr).filter(models.CountryHdr.country_id == country_id).first()
    if db_country:
        for key, value in country_update.dict(exclude_unset=True).items():
            setattr(db_country, key, value)
        db_country.modified_by = modified_by
        db.commit()
        db.refresh(db_country)
        return db_country
    return None

def deactivate_country(db: Session, country_id: int, modified_by: int):
    """Deactivates a country."""
    db_country = db.query(models.CountryHdr).filter(models.CountryHdr.country_id == country_id).first()
    if db_country:
        db_country.is_active = False
        db_country.modified_by = modified_by
        db.commit()
        return True
    return False