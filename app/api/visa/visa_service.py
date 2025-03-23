# app/api/visa/visa_service.py
from sqlalchemy.orm import Session
from ... import models
from . import visa_types
from typing import List, Optional
from datetime import datetime

def create_visa_process(db: Session, visa_process: visa_types.VisaProcessCreate, created_by: int):
    """Creates a new visa process."""
    db_visa_process = models.VisaProcessHdr(
        process_name=visa_process.process_name,
        visa_code=visa_process.visa_code,
        country_fee=visa_process.country_fee,
        visa_description=visa_process.visa_description,
        vendor_commission=visa_process.vendor_commission,
        country_id=visa_process.country_id,
        created_by=created_by,
    )
    db.add(db_visa_process)
    db.commit()
    db.refresh(db_visa_process)

    # Add fields (if any)
    if visa_process.fields:
        for field in visa_process.fields:
            db_field = models.VisaField(
                visa_process_id=db_visa_process.visa_process_id,
                binding_key=field.binding_key,
                field_name=field.field_name,
                field_type=field.field_type,
                validation_type=field.validation_type,
                validation_rule=field.validation_rule,
                error_message=field.error_message,
            )
            db.add(db_field)

    # Add rate cuts (if any)
    if visa_process.rate_cuts:
        for rate_cut in visa_process.rate_cuts:
            db_rate_cut = models.VisaRateCut(
                visa_process_id=db_visa_process.visa_process_id,
                government_fee=rate_cut.government_fee,
                service_fee=rate_cut.service_fee,
                tax=rate_cut.tax,
                start_date=rate_cut.start_date,
                end_date=rate_cut.end_date,
                is_default=rate_cut.is_default,
                created_by=created_by,
            )
            db.add(db_rate_cut)

    # Add media files (if any)
    if visa_process.media_files:
        for media in visa_process.media_files:
            db_media = models.CountryServiceMedia(
                visa_process_id=db_visa_process.visa_process_id,
                file_path=media.file_path,
                file_type=media.file_type,
                is_default=media.is_default,
                uploaded_at=datetime.now(),
            )
            db.add(db_media)

    db.commit()
    return db_visa_process

def get_visa_process(db: Session, visa_process_id: int):
    """Retrieves a visa process by its ID."""
    return db.query(models.VisaProcessHdr).filter(models.VisaProcessHdr.visa_process_id == visa_process_id).first()

def get_all_visa_processes(
    db: Session,
    country_id: Optional[int] = None,
    process_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """Retrieves all visa processes with optional filters."""
    query = db.query(models.VisaProcessHdr)
    if country_id:
        query = query.filter(models.VisaProcessHdr.country_id == country_id)
    if process_name:
        query = query.filter(models.VisaProcessHdr.process_name.ilike(f"%{process_name}%"))
    total_count = query.count()
    visa_processes = query.offset(skip).limit(limit).all()
    return visa_processes, total_count

def update_visa_process(db: Session, visa_process_id: int, visa_process_update: visa_types.VisaProcessUpdate, modified_by: int):
    """Updates an existing visa process."""
    db_visa_process = db.query(models.VisaProcessHdr).filter(models.VisaProcessHdr.visa_process_id == visa_process_id).first()
    if db_visa_process:
        update_data = visa_process_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_visa_process, key, value)
        db_visa_process.modified_by = modified_by
        db.commit()
        db.refresh(db_visa_process)
        return db_visa_process
    return None

def deactivate_visa_process(db: Session, visa_process_id: int, modified_by: int):
    """Deactivates a visa process."""
    db_visa_process = db.query(models.VisaProcessHdr).filter(models.VisaProcessHdr.visa_process_id == visa_process_id).first()
    if db_visa_process:
        db_visa_process.is_active = False
        db_visa_process.modified_by = modified_by
        db.commit()
        return True
    return False

def create_rate_cut(db: Session, visa_process_id: int, rate_cut: visa_types.VisaRateCutCreate, created_by: int):
    """Creates a new rate cut for a visa process."""
    # Ensure only one default rate cut
    if rate_cut.is_default:
        db.query(models.VisaRateCut).filter(
            models.VisaRateCut.visa_process_id == visa_process_id,
            models.VisaRateCut.is_default == True,
        ).update({"is_default": False})

    db_rate_cut = models.VisaRateCut(
        visa_process_id=visa_process_id,
        government_fee=rate_cut.government_fee,
        service_fee=rate_cut.service_fee,
        tax=rate_cut.tax,
        start_date=rate_cut.start_date,
        end_date=rate_cut.end_date,
        is_default=rate_cut.is_default,
        created_by=created_by,
    )
    db.add(db_rate_cut)
    db.commit()
    db.refresh(db_rate_cut)
    return db_rate_cut

def update_rate_cut(db: Session, rate_cut_id: int, rate_cut_update: visa_types.VisaRateCutUpdate, modified_by: int):
    """Updates an existing rate cut."""
    db_rate_cut = db.query(models.VisaRateCut).filter(models.VisaRateCut.visa_rate_cut_id == rate_cut_id).first()
    if db_rate_cut:
        # Ensure only one default rate cut
        if rate_cut_update.is_default:
            db.query(models.VisaRateCut).filter(
                models.VisaRateCut.visa_process_id == db_rate_cut.visa_process_id,
                models.VisaRateCut.is_default == True,
            ).update({"is_default": False})

        update_data = rate_cut_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rate_cut, key, value)
        db_rate_cut.modified_by = modified_by
        db.commit()
        db.refresh(db_rate_cut)
        return db_rate_cut
    return None

def get_all_fields(db: Session, visa_process_id: int):
    """Retrieves all fields for a visa process."""
    return db.query(models.VisaField).filter(models.VisaField.visa_process_id == visa_process_id).all()

def update_field(db: Session, field_id: int, field_update: visa_types.VisaFieldUpdate, modified_by: int):
    """Updates an existing field in a visa process."""
    db_field = db.query(models.VisaField).filter(models.VisaField.field_id == field_id).first()
    if db_field:
        update_data = field_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_field, key, value)
        db_field.modified_by = modified_by
        db.commit()
        db.refresh(db_field)
        return db_field
    return None