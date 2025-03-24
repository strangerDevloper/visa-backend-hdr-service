# app/models/country_service_media.py

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class CountryServiceMedia(Base):
    __tablename__ = "country_service_media"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("country_hdr.country_id"), nullable=True)  # Optional for visa_process media
    visa_process_id = Column(Integer, ForeignKey("visa_process_hdr.visa_process_id"), nullable=True)  # Optional for country media
    file_name = Column(String(255), nullable=False)  # Name of the file (e.g., "flag.jpg")
    file_path = Column(String(255), nullable=False)  # Full path or URL of the file (e.g., "https://s3.amazonaws.com/flag.jpg")
    file_type = Column(Enum("IMAGE", "VIDEO", name="file_type_enum"), nullable=False)  # Type of file (image or video)
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)  # Timestamp of upload
    is_flag = Column(Boolean, default=False, nullable=False)  # Whether the file is a country flag
    is_icon = Column(Boolean, default=False, nullable=False)  # Whether the file is a country icon
    is_default = Column(Boolean, default=False, nullable=False)  # Whether the file is the default media

    # Relationships
    country = relationship("CountryHdr", back_populates="media")  # Link to the CountryHdr model
    visa_process = relationship("VisaProcessHdr", back_populates="media")  # Link to the VisaProcessHdr model