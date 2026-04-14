"""
Notifications routes: list and mark-as-read.

Notifications are stored in a dedicated DynamoDB table when files
are shared with a user. The SNS email is separate (push); these are
the in-app notification records.
"""

from fastapi import APIRouter, HTTPException, Depends, status

from cloudshare import MetadataManager
from app.config import settings
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Uses the notifications table (pk=recipient_email, sk=notification_id)
notif_db = MetadataManager(
    table_name=settings.DYNAMO_NOTIF_TABLE,
    pk_name="recipient_email",
    sk_name="notification_id",
    region=settings.AWS_REGION,
)


@router.get("/")
async def list_notifications(current_user: dict = Depends(get_current_user)):
    """Return all notifications for the current user.

    Notifications are created by the SQS worker when files are shared.
    Results are ordered newest-first by the 'timestamp' field.
    """
    user_email = current_user.get("email", current_user["username"])
    notifications = notif_db.query_items(user_email)
    # Sort newest first
    notifications.sort(key=lambda n: n.get("timestamp", ""), reverse=True)
    unread_count = sum(1 for n in notifications if not n.get("read", False))
    return {"notifications": notifications, "unread_count": unread_count}


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_as_read(
    notification_id: str, current_user: dict = Depends(get_current_user)
):
    """Mark a specific notification as read.

    Args:
        notification_id: The sort key of the notification to mark.
    """
    user_email = current_user.get("email", current_user["username"])

    record = notif_db.get_item(user_email, notification_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notif_db.update_item(user_email, notification_id, {"read": True})
    return {"message": "Notification marked as read."}
