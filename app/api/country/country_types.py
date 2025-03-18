# app/api/country/country_types.py
from typing import Optional
from pydantic import BaseModel

class CountryBase(BaseModel):
    country_name: str
    country_code: str
    logo_path: Optional[str] = None

class CountryCreate(CountryBase):
    pass

class CountryUpdate(CountryBase):
    country_name: Optional[str] = None
    country_code: Optional[str] = None

class Country(CountryBase):
    country_id: int
    is_active: bool

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
