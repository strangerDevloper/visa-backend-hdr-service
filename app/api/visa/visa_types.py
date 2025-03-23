# app/api/visa/visa_types.py
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class VisaMediaCreate(BaseModel):
    """Payload for adding a media file to a visa process."""
    file_path: str  # S3 file path
    file_type: str  # "IMAGE" or "VIDEO"
    is_default: bool = False  # Whether the file is the default media

class VisaFieldCreate(BaseModel):
    """Payload for adding a field to a visa process."""
    binding_key: str
    field_name: str
    field_type: str  # "STRING", "NUMBER", "DOCUMENT", "BOOLEAN"
    validation_type: Optional[str] = None  # "REGEX", "STRING", "INPUT"
    validation_rule: Optional[str] = None
    error_message: Optional[str] = None

class VisaFieldUpdate(BaseModel):
    """Payload for updating a field in a visa process."""
    binding_key: Optional[str] = None
    field_name: Optional[str] = None
    field_type: Optional[str] = None
    validation_type: Optional[str] = None
    validation_rule: Optional[str] = None
    error_message: Optional[str] = None

class VisaRateCutCreate(BaseModel):
    """Payload for adding a rate cut to a visa process."""
    government_fee: int
    service_fee: int
    tax: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_default: bool = False  # Whether the rate cut is the default

class VisaRateCutUpdate(BaseModel):
    """Payload for updating a rate cut in a visa process."""
    government_fee: Optional[int] = None
    service_fee: Optional[int] = None
    tax: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_default: Optional[bool] = None

class VisaProcessCreate(BaseModel):
    """Payload for creating a visa process."""
    process_name: str
    visa_code: str
    country_fee: int
    visa_description: Optional[str] = None
    vendor_commission: float = Field(..., gt=0, le=100)  # Percentage (0-100)
    country_id: int
    fields: Optional[List[VisaFieldCreate]] = None  # Optional fields
    rate_cuts: Optional[List[VisaRateCutCreate]] = None  # Optional rate cuts
    media_files: Optional[List[VisaMediaCreate]] = None  # Optional media files

class VisaProcessUpdate(BaseModel):
    """Payload for updating a visa process."""
    process_name: Optional[str] = None
    visa_code: Optional[str] = None
    country_fee: Optional[int] = None
    visa_description: Optional[str] = None
    vendor_commission: Optional[float] = Field(None, gt=0, le=100)
    is_active: Optional[bool] = None
    fields: Optional[List[VisaFieldCreate]] = None
    rate_cuts: Optional[List[VisaRateCutCreate]] = None
    media_files: Optional[List[VisaMediaCreate]] = None

class VisaProcess(BaseModel):
    """Response model for a visa process."""
    visa_process_id: int
    process_name: str
    visa_code: str
    country_fee: int
    visa_description: Optional[str] = None
    vendor_commission: float
    is_active: bool
    created_date: datetime
    modified_date: Optional[datetime] = None
    country_id: int
    created_by: int
    modified_by: Optional[int] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models