"""
File management routes: upload, list, download, delete.

Files are stored in S3; metadata is persisted in DynamoDB.
All routes require a valid Cognito JWT (Bearer token).
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from botocore.exceptions import ClientError

from cloudshare import StorageManager, MetadataManager
from app.config import settings
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/files", tags=["files"])

# Shared AWS service instances
storage = StorageManager(bucket_name=settings.S3_BUCKET, region=settings.AWS_REGION)
db = MetadataManager(
    table_name=settings.DYNAMO_FILES_TABLE,
    pk_name="user_id",
    sk_name="file_id",
    region=settings.AWS_REGION,
)

# Maximum allowed file size: 100 MB
MAX_FILE_SIZE = 100 * 1024 * 1024


@router.get("/")
async def list_files(current_user: dict = Depends(get_current_user)):
    """List all files uploaded by the current user.

    Queries DynamoDB for file metadata belonging to the authenticated user.
    Does not return files shared with the user (use /api/share/received).
    """
    user_id = current_user["username"]
    files = db.query_items(user_id)
    return {"files": files}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload a file to S3 and record its metadata in DynamoDB.

    The file is stored under a user-specific prefix in S3:
    `uploads/{user_id}/{file_id}/{original_filename}`

    Args:
        file: Multipart file from the request body.
        current_user: JWT claims of the authenticated user.

    Returns:
        The stored file metadata record.
    """
    user_id = current_user["username"]
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{user_id}/{file_id}/{file.filename}"

    # Validate file size by reading content (FastAPI UploadFile is lazy)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 100 MB limit.")

    # Seek back so upload_fileobj can read from the start
    await file.seek(0)

    try:
        storage.upload_file(file.file, s3_key, file.content_type or "application/octet-stream")
    except ClientError as exc:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {exc}")

    # Build and store metadata record in DynamoDB
    metadata = {
        "user_id": user_id,
        "file_id": file_id,
        "filename": file.filename,
        "s3_key": s3_key,
        "size": len(content),
        "content_type": file.content_type or "application/octet-stream",
        "upload_time": datetime.now(timezone.utc).isoformat(),
        "shared_with": [],
    }
    db.put_item(metadata)

    return {"message": "File uploaded successfully.", "file": metadata}


@router.get("/{file_id}/download")
async def download_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Generate a presigned S3 URL to download a specific file.

    The URL expires in 1 hour and can be opened directly in a browser.
    The user must own the file or have it shared with them.
    """
    user_id = current_user["username"]

    # Try to fetch as owner first
    record = db.get_item(user_id, file_id)

    # If not found as owner, check if shared with this user
    if record is None:
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        url = storage.generate_presigned_url(record["s3_key"], expiry=3600)
    except ClientError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {exc}")

    return {"download_url": url, "filename": record["filename"], "expires_in": 3600}


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a file from S3 and remove its metadata from DynamoDB.

    Only the file owner can delete a file.
    """
    user_id = current_user["username"]

    record = db.get_item(user_id, file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="File not found.")

    # Delete from S3
    storage.delete_file(record["s3_key"])

    # Delete metadata from DynamoDB
    db.delete_item(user_id, file_id)

    return {"message": f"File '{record['filename']}' deleted successfully."}
