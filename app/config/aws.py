# app/services/aws_service.py

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from fastapi import HTTPException, UploadFile, status
import uuid

class AWSService:
    def __init__(self):
        """
        Initialize the AWS S3 client using environment variables.
        """
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = os.getenv("AWS_REGION_NAME", "us-south-1")  # Default to 'us-east-1'
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")

        # Validate that all required environment variables are set
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            raise ValueError("AWS credentials or bucket name not found in environment variables")

        # Initialize the S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def upload_file(self, file_path: str, folder_path: str = ""):
        """
        Upload a file to the specified folder in the S3 bucket.
        
        :param file_path: Path to the file to upload
        :param folder_path: Folder path in the S3 bucket (e.g., 'images/')
        :return: S3 object URL
        """
        try:
            # Extract the file name from the file path
            file_name = os.path.basename(file_path)

            # Define the S3 object key (folder_path + file_name)
            s3_object_key = os.path.join(folder_path, file_name) if folder_path else file_name

            # Upload the file
            self.s3_client.upload_file(file_path, self.bucket_name, s3_object_key)

            # Generate the S3 object URL
            object_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_object_key}"
            return object_url

        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS credentials not found"
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AWS Client Error: {str(e)}"
            )
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL to access a private S3 object
        Args:
            s3_key: The S3 object key (e.g., 'countries/US/abc123.jpg')
            expiration: URL validity in seconds (default: 1 hour)
        Returns:
            Presigned URL as string
        Raises:
            HTTPException: If URL generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            error_msg = f"AWS Client Error generating presigned URL: {str(e)}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error generating presigned URL: {str(e)}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        # app/services/aws_service.py
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        Args:
            s3_key: Full S3 path (e.g., 'countries/US/abc123.jpg')
        Returns:
            bool: True if successful
        Raises:
            HTTPException: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 deletion failed: {str(e)}"
            )

    def replace_file(self, old_s3_key: str, new_file: UploadFile) -> str:
        """
        Replace a file in S3 while keeping the same path
        Args:
            old_s3_key: Existing S3 path
            new_file: New file to upload
        Returns:
            str: New presigned URL
        """
        try:
            # Delete old file
            self.delete_file(old_s3_key)
            
            # Upload new file to same path
            new_file.file.seek(0)
            self.s3_client.upload_fileobj(
                new_file.file,
                self.bucket_name,
                old_s3_key
            )
            return self.generate_presigned_url(old_s3_key)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File replacement failed: {str(e)}"
            )

    def generate_country_media_path(self, country_code: str) -> str:
        """Generates path: countries/{country_code}/{fuid}"""
        fuid = str(uuid.uuid4())
        return f"countries/{country_code}/{fuid}"
    
    def generate_visa_media_path(self, country_code: str, visa_short_name: str) -> str:
        """Generates path: visa/{country_code}/{visa_short_name}/{fuid}"""
        fuid = str(uuid.uuid4())
        return f"visa/{country_code}/{visa_short_name}/{fuid}"