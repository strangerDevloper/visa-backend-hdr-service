# app/api/country/country_routes.py
from datetime import datetime
import hashlib
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Union, Optional

from app import models
from app.config.aws import AWSService
from ...config.database import get_db
from . import country_types, country_service
from ...api.dependencies import CurrentEmployee

router = APIRouter(prefix="/countries", tags=["countries"])

# Initialize the AWS Service
aws_service = AWSService()

@router.post("/", response_model=country_types.Country, status_code=status.HTTP_201_CREATED)
def create_country(
    country: country_types.CountryCreate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """
    Creates a new country.
    - Media files are optional.
    - Each media file includes `file_path`, `is_flag`, and `is_icon`.
    """
    try:
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

        # Create the country
        db_country = country_service.create_country(db, country, current_employee.employee_id)

        # # Handle media files (if any)
        # if country.media_files:
        #     for media in country.media_files:
        #         country_service.add_country_media(db, db_country.country_id, media, current_employee.employee_id)

        return db_country

    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTP exceptions
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the country: {str(e)}"
        )

@router.get("/{country_id}", response_model=country_types.CountryWithMedia)
def get_country(
    country_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Retrieves a country by its ID along with its media."""
    db_country = country_service.get_country(db, country_id)
    if not db_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    # Fetch media files for the country
    media_files = country_service.get_country_media(db, country_id)

    media_files_with_presigned_urls = []
    for media in media_files:
        media_files_with_presigned_urls.append({
            "image_id": media.image_id,
            "presigned_url": aws_service.generate_presigned_url(media.file_path),
            "file_path" : media.file_path,
            "is_flag": media.is_flag,
            "is_icon": media.is_icon,
            "expires_in": "3600 seconds"
        })

    return {"country": db_country, "media_files": media_files_with_presigned_urls}

@router.get("/", response_model=Dict[str, Union[List[country_types.Country], int]])
def get_countries(
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
    is_active: Union[bool, None] = Query(None, description="Filter by active status (true/false)"),
    search: str = Query(None, description="Search by country name"),
):
    """Retrieves a list of countries with pagination, optional filtering, and search by name."""
    countries, total_count = country_service.get_countries_paginated(
        db, skip=skip, limit=limit, is_active=is_active, search=search
    )
    return {"countries": countries, "total_count": total_count}

@router.put("/{country_id}", response_model=country_types.Country)
def update_country(
    country_id: int,
    country_update: country_types.CountryUpdate,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Updates an existing country with details and optional media files."""
    db_country = country_service.get_country(db, country_id)
    if not db_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    # Update country details
    updated_country = country_service.update_country(db, country_id, country_update, current_employee.employee_id)

    # # Handle media files (if any)
    # if country_update.media_files:
    #     for media in country_update.media_files:
    #         country_service.add_country_media(db, country_id, media, current_employee.employee_id)

    return updated_country

@router.delete("/{country_id}", status_code=status.HTTP_200_OK)
def delete_country(
    country_id: int,
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db),
):
    """Deactivates a country."""
    try:
        db_country = country_service.get_country(db, country_id)
        if not db_country:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
        
        country_service.deactivate_country(db, country_id, current_employee.employee_id)
        return {"message": "Country deactivated successfully"}
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTP exceptions
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{country_id}/upload-media")
async def upload_country_media(
    current_employee: CurrentEmployee,
    country_id: int,
    files: List[UploadFile] = File(...),
    is_flag: bool = False,
    is_icon: bool = False,
    is_default: bool = False,
    db: Session = Depends(get_db)
):
    try:
        country = db.query(models.CountryHdr).get(country_id)
        if not country:
            raise HTTPException(404, "Country not found")

        results = []
        for file in files:
            # Generate unique filename
            file_ext = file.filename.split('.')[-1].lower()
            file_hash = hashlib.md5(f"{datetime.now().timestamp()}{file.filename}".encode()).hexdigest()
            s3_key = f"countries/{country.country_code}/{file_hash}.{file_ext}"

            # Upload to S3
            file.file.seek(0)
            aws_service.s3_client.upload_fileobj(
                file.file,
                aws_service.bucket_name,
                s3_key
            )

            # Save to DB
            media = models.CountryServiceMedia(
                country_id=country_id,
                file_name=file.filename,
                file_path=s3_key,  # Store only the S3 key
                file_type="IMAGE" if file.content_type.startswith("image") else "VIDEO",
                is_flag=is_flag,
                is_icon=is_icon,
                is_default=is_default
            )
            db.add(media)
            results.append({"media_id": media.image_id, "s3_key": s3_key})

        db.commit()
        return {"success_count": len(results), "uploads": results}

    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))
    

@router.get("/media/{country_id}")  # Changed to path parameter
def get_media_with_presigned_urls(
    country_id: int,  # Now a required path parameter
    current_employee: CurrentEmployee,
    db: Session = Depends(get_db)
):
    query = db.query(models.CountryServiceMedia).filter(
        models.CountryServiceMedia.country_id == country_id
    )
    
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

@router.get("/media/{media_id}/url")
def get_presigned_url(media_id: int, db: Session = Depends(get_db)):
    media = db.query(models.CountryServiceMedia).get(media_id)
    if not media:
        raise HTTPException(404, "Media not found")
    return {
        "url": aws_service.generate_presigned_url(media.file_path),
        "expires_in": "3600 seconds"
    }


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