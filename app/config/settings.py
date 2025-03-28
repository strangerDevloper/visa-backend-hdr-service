# app/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: PostgresDsn = Field(
        ...,
        example="postgresql://user:password@localhost:5432/dbname",
        description="PostgreSQL connection URL"
    )
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        ...,
        min_length=5,
        description="Secret key for JWT token signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = Field(
        ...,
        description="AWS IAM access key ID"
    )
    AWS_SECRET_ACCESS_KEY: str = Field(
        ...,
        description="AWS IAM secret access key"
    )
    AWS_REGION_NAME: str = Field(
        default="ap-south-1",
        description="AWS service region"
    )
    AWS_BUCKET_NAME: str = Field(
        ...,
        description="S3 bucket name for storage"
    )
    
    # SMTP Configuration
    SMTP_SERVER: str = Field(
        ...,
        description="SMTP server hostname"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP server port"
    )
    SMTP_USERNAME: str = Field(
        ...,
        description="SMTP authentication username"
    )
    SMTP_PASSWORD: str = Field(
        ...,
        description="SMTP authentication password"
    )
    SENDER_EMAIL: str = Field(
        ...,
        description="Default sender email address"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'forbid'  # Prevent typos in env variables

# Create settings instance
settings = Settings()