"""
StorageManager: OOP wrapper for Amazon S3 file operations.

Handles file upload, download (presigned URLs), deletion,
and listing within a specified S3 bucket.
"""

import boto3
from botocore.exceptions import ClientError


class StorageManager:
    """Manages file storage operations using Amazon S3.

    Attributes:
        bucket_name (str): The S3 bucket where files are stored.
        region (str): AWS region of the S3 bucket.
        client (boto3.client): The underlying boto3 S3 client.
    """

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """Initialise the StorageManager with an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket to operate on.
            region: AWS region string (default 'us-east-1').
        """
        self.bucket_name = bucket_name
        self.region = region
        # boto3 picks up credentials from the EC2 IAM role automatically
        self.client = boto3.client("s3", region_name=region)

    def upload_file(self, file_obj, s3_key: str, content_type: str = "application/octet-stream") -> str:
        """Upload a file-like object to S3.

        Args:
            file_obj: File-like object (e.g. SpooledTemporaryFile from FastAPI).
            s3_key: Destination key (path) within the bucket.
            content_type: MIME type of the file.

        Returns:
            The s3_key of the uploaded object.

        Raises:
            ClientError: If the S3 upload fails.
        """
        self.client.upload_fileobj(
            file_obj,
            self.bucket_name,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        return s3_key

    def generate_presigned_url(self, s3_key: str, expiry: int = 3600) -> str:
        """Generate a presigned URL for downloading a file.

        The URL is time-limited and does not require AWS credentials
        for the downloader.

        Args:
            s3_key: The S3 object key to generate a URL for.
            expiry: Seconds until the URL expires (default 3600 = 1 hour).

        Returns:
            A presigned HTTPS download URL.

        Raises:
            ClientError: If URL generation fails.
        """
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expiry,
        )
        return url

    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3.

        Args:
            s3_key: The S3 object key to delete.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

    def list_files(self, prefix: str = "") -> list:
        """List all objects in the bucket under a given prefix.

        Args:
            prefix: Key prefix to filter results (e.g. a user's folder).

        Returns:
            List of dicts with 'key', 'size', and 'last_modified' fields.
        """
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        objects = []
        for obj in response.get("Contents", []):
            objects.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            })
        return objects
