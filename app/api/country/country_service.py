# app/api/country/country_service.py
from sqlalchemy.orm import Session
from ... import models
from . import country_types
from typing import List, Union, Optional

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
        currency=country.currency,
        official_language=country.official_language,
        description=country.description,
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

def get_countries_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    is_active: Union[bool, None] = None,
    search: Optional[str] = None,
):
    """Retrieves a list of countries with pagination, optional filtering, and search by name."""
    query = db.query(models.CountryHdr)
    if is_active is not None:
        query = query.filter(models.CountryHdr.is_active == is_active)
    if search:
        query = query.filter(models.CountryHdr.country_name.ilike(f"%{search}%"))
    total_count = query.count()
    countries = query.offset(skip).limit(limit).all()
    return countries, total_count

def update_country(db: Session, country_id: int, country_update: country_types.CountryUpdate, modified_by: int):
    """Updates an existing country with details."""
    db_country = db.query(models.CountryHdr).filter(models.CountryHdr.country_id == country_id).first()
    if db_country:
        # Update fields provided in the payload
        update_data = country_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_country, key, value)

        # Explicitly handle `is_active` if it is provided in the payload
        if "is_active" in update_data:
            db_country.is_active = update_data["is_active"]
        
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

def get_country_media(db: Session, country_id: int):
    """Retrieves media files for a country."""
    return db.query(models.CountryServiceMedia).filter(
        models.CountryServiceMedia.country_id == country_id
    ).all()

def add_country_media(db: Session, country_id: int, media: country_types.CountryMediaCreate, modified_by: int):
    """Adds a media file for a country."""
    db_media = models.CountryServiceMedia(
        country_id=country_id,
        file_path=media.file_path,
        is_flag=media.is_flag,
        is_icon=media.is_icon,
        modified_by=modified_by,
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media