# app/api/visa/visa_routes.py
from datetime import datetime
import hashlib
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union

from app import models
from app.config.aws import AWSService

from ...config.database import get_db
from . import visa_types, visa_service
from ...api.dependencies import CurrentEmployee

router = APIRouter(prefix="/visa", tags=["visa"])

aws_service = AWSService()

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


@router.post("/{visa_process_id}/upload-media")
async def upload_visa_media(
    current_employee: CurrentEmployee,
    visa_process_id: int,
    files: List[UploadFile] = File(...),
    is_default: bool = False,
    db: Session = Depends(get_db)
):
    try:
        # Get visa process details
        visa_process = db.query(models.VisaProcessHdr).get(visa_process_id)
        if not visa_process:
            raise HTTPException(404, "Visa process not found")

        # Get country code
        country = db.query(models.CountryHdr).get(visa_process.country_id)
        if not country:
            raise HTTPException(404, "Country not found")

        results = []
        for file in files:
            # Generate hashed filename
            file_ext = file.filename.split('.')[-1].lower()
            file_hash = hashlib.md5(f"{datetime.now().timestamp()}{file.filename}".encode()).hexdigest()
            s3_key = f"visa/{country.country_code}/{visa_process.visa_code}/{file_hash}.{file_ext}"
            
            # Upload to S3
            file.file.seek(0)
            aws_service.s3_client.upload_fileobj(
                file.file,
                aws_service.bucket_name,
                s3_key
            )

            # Insert into DB
            media = models.CountryServiceMedia(
                visa_process_id=visa_process_id,
                file_name=file.filename,  # Store original filename
                file_path=s3_key,        # Store only S3 key
                file_type="IMAGE" if file.content_type.startswith("image") else "VIDEO",
                is_default=is_default,
                modified_by=current_employee.employee_id
            )
            db.add(media)
            results.append({
                "media_id": media.image_id,
                "s3_key": s3_key,
                "original_filename": file.filename,
                "file_type": media.file_type
            })
        
        db.commit()
        return {
            "success_count": len(results),
            "uploads": results
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))
    
@router.get("/media")
def get_media_with_presigned_urls(
    current_employee: CurrentEmployee,
    visa_process_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if not visa_process_id:
        raise HTTPException(400, "visa_process_id must be provided")

    query = db.query(models.CountryServiceMedia)
    if visa_process_id:
        query = query.filter(models.CountryServiceMedia.visa_process_id == visa_process_id)

    media_items = query.all()
    
    results = []
    for media in media_items:
        results.append({
            "media_id": media.image_id,
            "original_filename": media.file_name,
            "presigned_url": aws_service.generate_presigned_url(media.file_path),
            "file_type": media.file_type,
            "is_flag": media.is_flag,
            "is_icon": media.is_icon,
            "is_default": media.is_default,
            "uploaded_at": media.uploaded_at.isoformat(),
            "expires_in": "3600 seconds"
        })

    return {"media_items": results}



@router.put("/media/{media_id}/replace")
async def replace_media(
    current_employee: CurrentEmployee,
    media_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Replace an existing media file while keeping the same S3 path
    """
    try:
        # Get existing media record
        media = db.query(models.CountryServiceMedia).get(media_id)
        if not media:
            raise HTTPException(404, "Media not found")

        # Replace file in S3
        new_url = aws_service.replace_file(
            old_s3_key=media.file_path,
            new_file=file
        )

        # Update database record
        media.file_name = file.filename
        media.file_type = "IMAGE" if file.content_type.startswith("image") else "VIDEO"
        media.modified_by = current_employee.employee_id
        media.uploaded_at = datetime.now()
        
        db.commit()
        
        return {
            "message": "File replaced successfully",
            "new_presigned_url": new_url,
            "media_id": media_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))
    
@router.delete("/media/{media_id}")
async def delete_media(
    media_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    """
    Delete a media file and its database record
    """
    try:
        media = db.query(models.CountryServiceMedia).get(media_id)
        if not media:
            raise HTTPException(404, "Media not found")

        # Delete from S3
        aws_service.delete_file(media.file_path)
        
        # Delete database record
        db.delete(media)
        db.commit()
        
        return {"message": "Media deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))