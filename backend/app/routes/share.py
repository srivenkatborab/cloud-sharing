"""
File sharing route.

When a user shares a file, the request is placed on an SQS queue.
A background worker (share_worker.py) processes the queue asynchronously:
it records the share in DynamoDB and triggers an SNS email notification.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from cloudshare import QueueManager, MetadataManager
from app.config import settings
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/share", tags=["share"])

# Shared service instances
queue = QueueManager(queue_url=settings.SQS_QUEUE_URL, region=settings.AWS_REGION)
db = MetadataManager(
    table_name=settings.DYNAMO_FILES_TABLE,
    pk_name="user_id",
    sk_name="file_id",
    region=settings.AWS_REGION,
)


class ShareRequest(BaseModel):
    file_id: str
    recipient_email: EmailStr


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def share_file(body: ShareRequest, current_user: dict = Depends(get_current_user)):
    """Share a file with another user.

    Validates that the file belongs to the current user, then places
    a share task on the SQS queue for async processing.

    Returns HTTP 202 Accepted — the actual share and notification happen
    in the background via the SQS worker.
    """
    user_id = current_user["username"]
    sharer_email = current_user.get("email", user_id)

    # Verify the file exists and belongs to the requester
    record = db.get_item(user_id, body.file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="File not found or you do not own it.")

    if body.recipient_email == sharer_email:
        raise HTTPException(status_code=400, detail="You cannot share a file with yourself.")

    # Enqueue the share task — worker handles the rest asynchronously
    message_id = queue.send_message({
        "action": "share_file",
        "file_id": body.file_id,
        "file_owner_id": user_id,
        "sharer_email": sharer_email,
        "recipient_email": body.recipient_email,
        "filename": record["filename"],
        "s3_key": record["s3_key"],
    })

    return {
        "message": f"Share request queued. {body.recipient_email} will be notified shortly.",
        "queue_message_id": message_id,
    }
