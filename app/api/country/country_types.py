# app/api/country/country_types.py
from typing import List, Optional
from pydantic import BaseModel

class CountryMediaCreate(BaseModel):
    """Payload for adding a media file to a country."""
    file_path: str  # S3 file path
    is_flag: bool = False  # Whether the file is a country flag
    is_icon: bool = False  # Whether the file is a country icon

class CountryBase(BaseModel):
    country_name: str
    country_code: str
    currency: Optional[str] = None
    official_language: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None

class CountryCreate(CountryBase):
    """Payload for creating a country."""
    media_files: Optional[List[CountryMediaCreate]] = None  # Optional media files

class CountryUpdate(BaseModel):
    """Payload for updating a country. All fields are optional."""
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    currency: Optional[str] = None
    official_language: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    is_active: Optional[bool] = None
    media_files: Optional[List[CountryMediaCreate]] = None  # Optional media files

class Country(CountryBase):
    """Response model for a country."""
    country_id: int
    is_active: bool

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

class CountryWithMedia(BaseModel):
    """Response model for a country with media files."""
    country: Country
    media_files: List[CountryMediaCreate]  # List of media files