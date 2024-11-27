import re

from app.core.services.base import FileService

from pathlib import Path
from fastapi import UploadFile
from botocore.exceptions import BotoCoreError, ClientError


class S3Service(FileService):
    def __init__(self, is_local="development", s3_client=None, bucket_name=None, local_storage_dir="uploads",
                 static_endpoint="/static/uploads"):
        """
        Initialize the file service for managing files locally or on S3.
        """
        self.is_local = is_local == "development"
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.local_storage_dir = local_storage_dir
        self.static_endpoint = static_endpoint

        if not self.s3_client and not self.is_local:
            raise ValueError("Either s3_client must be provided or is_local must be True")

        if not self.is_local:
            Path(self.local_storage_dir).mkdir(parents=True, exist_ok=True)

    def upload_file(self, file: UploadFile, key: str) -> str:
        """Upload file to S3 or local storage."""
        if self.is_local:
            # Local file upload
            file_path = Path(self.local_storage_dir) / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            return f"{self.static_endpoint}/{key}"

        else:
            # S3 upload
            try:
                self.s3_client.upload_fileobj(file.file, self.bucket_name, key)
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            except (BotoCoreError, ClientError) as e:
                raise Exception(f"S3 upload failed: {str(e)}")

    def delete_file(self, file_url: str):
        """
        Delete file from S3 or local storage based on the provided URL.
        If the URL is local (starts with static endpoint), delete it from local storage.
        If the URL is an S3 URL, delete the file from S3.
        """
        # Check if it's a local file URL or S3 URL
        if file_url.startswith(self.static_endpoint):
            # Local storage path
            file_path = Path(self.local_storage_dir) / file_url[len(self.static_endpoint) + 1:]
            if file_path.exists():
                file_path.unlink()
                return {"message": f"File '{file_url}' deleted successfully from local storage"}
            else:
                return {"message": f"File '{file_url}' not found in local storage"}
        elif "s3.amazonaws.com" in file_url:
            # Extract the S3 key from the URL (after the bucket name)
            s3_key = re.sub(r'https://[^/]+/([^/]+/.*)', r'\1', file_url)
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return {"message": f"File '{file_url}' deleted successfully from S3"}
            except (BotoCoreError, ClientError) as e:
                raise Exception(f"S3 deletion failed: {str(e)}")
        else:
            return {"message": "Invalid URL format for file deletion."}
