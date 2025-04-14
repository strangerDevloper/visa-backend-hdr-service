# app/api/visa/visa_types.py
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class FieldTypeEnum(str, Enum):
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    DOCUMENT = 'DOCUMENT'
    BOOLEAN = 'BOOLEAN'

class ValidationTypeEnum(str, Enum):
    REGEX = 'REGEX'
    STRING = 'STRING'
    INPUT = 'INPUT'

class VisaMediaCreate(BaseModel):
    """Payload for adding a media file to a visa process."""
    file_path: str  # S3 file path
    file_type: str  # "IMAGE" or "VIDEO"
    is_default: bool = False  # Whether the file is the default media

class VisaMediaResponse(BaseModel):
    """Payload for adding a media file to a country."""
    image_id: int  # Unique identifier for the media file
    file_path: str  # S3 file path
    is_flag: bool = False  # Whether the file is a country flag
    is_icon: bool = False  # Whether the file is a country icon
    presigned_url: str  # New field for the URL
    expires_in: str  # New field for the expiration time of the presigned URL


class VisaFieldCreate(BaseModel):
    """Payload for adding a field to a visa process."""
    binding_key: str = Field(..., min_length=1, max_length=50)
    field_name: str = Field(..., min_length=1, max_length=100)
    field_type: FieldTypeEnum  # Now using enum directly
    validation_type: Optional[ValidationTypeEnum] = None
    validation_rule: Optional[str] = Field(None, max_length=255)
    error_message: Optional[str] = Field(None, max_length=255)

    @validator('validation_rule')
    def validate_validation_rule(cls, v, values):
        if 'validation_type' in values and values['validation_type'] and not v:
            raise ValueError("validation_rule is required when validation_type is specified")
        return v

    @validator('error_message')
    def validate_error_message(cls, v, values):
        if 'validation_type' in values and values['validation_type'] and not v:
            raise ValueError("error_message is required when validation_type is specified")
        return v

class VisaFieldUpdate(BaseModel):
    """Payload for updating a field in a visa process."""
    binding_key: Optional[str] = None
    field_name: Optional[str] = None
    field_type: Optional[FieldTypeEnum] = None
    validation_type: Optional[ValidationTypeEnum] = None
    validation_rule: Optional[str] = None
    error_message: Optional[str] = None

    @validator('validation_rule')
    def validate_validation_rule(cls, v, values):
        if 'validation_type' in values and values['validation_type'] and not v:
            raise ValueError("validation_rule is required when validation_type is specified")
        return v

    @validator('error_message')
    def validate_error_message(cls, v, values):
        if 'validation_type' in values and values['validation_type'] and not v:
            raise ValueError("error_message is required when validation_type is specified")
        return v


class VisaFieldResponse(BaseModel):
    field_id: int
    binding_key: str
    field_name: str
    field_type: str
    validation_type: Optional[str] = None
    validation_rule: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

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

class VisaRateCutResponse(BaseModel):
    """Response model for a rate cut in a visa process."""
    visa_rate_cut_id: int
    government_fee: int
    service_fee: int
    tax: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_default: bool = False  # Whether the rate cut is the default
    created_date: datetime
    created_by: int

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models

class VisaProcessCreate(BaseModel):
    """Payload for creating a visa process."""
    process_name: str = Field(..., min_length=1, max_length=100)
    visa_code: str = Field(..., min_length=1, max_length=20)
    country_fee: int = Field(..., gt=0)
    visa_description: Optional[str] = Field(None, max_length=500)
    vendor_commission: float = Field(..., gt=0, le=100)  # Percentage (0-100)
    country_id: int = Field(..., gt=0)
    fields: Optional[List[VisaFieldCreate]] = None
    rate_cuts: Optional[List[VisaRateCutCreate]] = None

    class Config:
        use_enum_values = True  # This will store the enum values instead of enum objects

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
    # media_files: Optional[List[VisaMediaCreate]] = None

class VisaProcess(BaseModel):
    """Response model for a visa process."""
    visa_process_id: int
    process_name: str
    visa_code: str
    country_fee: int
    visa_description: Optional[str] = None
    vendor_commission: float
    created_date: datetime
    modified_date: Optional[datetime] = None
    country_id: int
    created_by: int
    modified_by: Optional[int] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class VisaProcessWithDetails(BaseModel):
    visa_process: VisaProcess  # Your existing VisaProcess model
    default_rate_cut: Optional[VisaRateCutResponse] = None  # Your VisaRateCut model
    visa_fields: List[VisaFieldResponse] = []
    media_files: List[VisaMediaResponse] = []