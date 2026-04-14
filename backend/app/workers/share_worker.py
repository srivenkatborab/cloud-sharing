"""
SQS background worker for processing file-share tasks.

Runs as a daemon thread inside the FastAPI process. Polls the SQS queue
every few seconds, processes share messages, updates DynamoDB, and sends
SNS email notifications to recipients.
"""

import threading
import logging
import uuid
from datetime import datetime, timezone

from cloudshare import QueueManager, MetadataManager, NotificationManager
from app.config import settings

logger = logging.getLogger(__name__)


def process_share_message(message: dict) -> None:
    """Handle a single file-share message from the SQS queue.

    Steps:
    1. Update the file record in DynamoDB to add the recipient.
    2. Write a notification record to the notifications table.
    3. Send an SNS email notification to the recipient.

    Args:
        message: Parsed message body dict from SQS.
    """
    file_id = message.get("file_id")
    file_owner_id = message.get("file_owner_id")
    sharer_email = message.get("sharer_email")
    recipient_email = message.get("recipient_email")
    filename = message.get("filename")

    # --- Step 1: Update file metadata to record the share ---
    files_db = MetadataManager(
        table_name=settings.DYNAMO_FILES_TABLE,
        pk_name="user_id",
        sk_name="file_id",
        region=settings.AWS_REGION,
    )
    file_record = files_db.get_item(file_owner_id, file_id)
    if file_record:
        current_shares = file_record.get("shared_with", [])
        if recipient_email not in current_shares:
            current_shares.append(recipient_email)
        files_db.update_item(file_owner_id, file_id, {"shared_with": current_shares})

    # --- Step 2: Create an in-app notification record in DynamoDB ---
    notif_db = MetadataManager(
        table_name=settings.DYNAMO_NOTIF_TABLE,
        pk_name="recipient_email",
        sk_name="notification_id",
        region=settings.AWS_REGION,
    )
    notification = {
        "recipient_email": recipient_email,
        "notification_id": str(uuid.uuid4()),
        "message": f"{sharer_email} shared '{filename}' with you.",
        "file_id": file_id,
        "file_owner_id": file_owner_id,
        "sharer_email": sharer_email,
        "filename": filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "read": False,
    }
    notif_db.put_item(notification)

    # --- Step 3: Send email notification via SNS ---
    notif_manager = NotificationManager(
        topic_arn=settings.SNS_TOPIC_ARN,
        region=settings.AWS_REGION,
    )
    try:
        notif_manager.send_file_share_notification(recipient_email, sharer_email, filename)
    except Exception as exc:
        # Log but do not crash — in-app notification was already created
        logger.warning(f"SNS notification failed for {recipient_email}: {exc}")

    logger.info(f"Share processed: {sharer_email} → {recipient_email} for file '{filename}'")


def run_worker(stop_event: threading.Event) -> None:
    """Main worker loop — polls SQS and dispatches messages.

    Args:
        stop_event: Set this event to gracefully stop the worker thread.
    """
    queue = QueueManager(queue_url=settings.SQS_QUEUE_URL, region=settings.AWS_REGION)
    logger.info("SQS share worker started.")

    while not stop_event.is_set():
        try:
            messages = queue.receive_messages(max_count=5, wait_seconds=5)
            for msg in messages:
                try:
                    process_share_message(msg["body"])
                except Exception as exc:
                    logger.error(f"Failed to process message: {exc}")
                finally:
                    # Always delete the message to avoid reprocessing
                    queue.delete_message(msg["receipt_handle"])
        except Exception as exc:
            logger.error(f"Worker poll error: {exc}")

    logger.info("SQS share worker stopped.")


def start_worker() -> tuple[threading.Thread, threading.Event]:
    """Start the SQS worker as a background daemon thread.

    Returns:
        Tuple of (thread, stop_event). Call stop_event.set() to stop.
    """
    stop_event = threading.Event()
    thread = threading.Thread(target=run_worker, args=(stop_event,), daemon=True)
    thread.start()
    return thread, stop_event
