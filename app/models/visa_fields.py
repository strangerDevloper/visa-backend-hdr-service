# app/models/visa_fields.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..config.database import Base

class FieldTypeEnum(PyEnum):
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    DOCUMENT = 'DOCUMENT'
    BOOLEAN = 'BOOLEAN'

class ValidationTypeEnum(PyEnum):
    REGEX = 'REGEX'
    STRING = 'STRING'
    INPUT = 'INPUT'

class VisaField(Base):
    __tablename__ = "visa_field"

    field_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    binding_key = Column(String)
    field_name = Column(String)
    field_type = Column(Enum(FieldTypeEnum))
    validation_type = Column(Enum(ValidationTypeEnum), nullable=True) # Validation type can be null
    validation_rule = Column(String, nullable=True) # Validation rule can be null
    error_message = Column(Text, nullable=True) # Error message can be null
    created_date = Column(DateTime, server_default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    visa_process_id = Column(Integer, ForeignKey('visa_process_hdr.visa_process_id'))

    visa_process = relationship("VisaProcessHdr")