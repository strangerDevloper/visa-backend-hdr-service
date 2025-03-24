# app/services/aws_service.py

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from fastapi import HTTPException, status

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