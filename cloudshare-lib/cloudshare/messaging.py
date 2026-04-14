"""
QueueManager: OOP wrapper for Amazon SQS operations.

Supports sending, receiving, and deleting messages from
an SQS Standard Queue to enable async processing.
"""

import json
import boto3
from botocore.exceptions import ClientError
from typing import Optional


class QueueManager:
    """Manages asynchronous messaging using Amazon SQS.

    Decouples the web tier from background processing tasks
    such as file-sharing operations.

    Attributes:
        queue_url (str): The full SQS queue URL.
        region (str): AWS region of the queue.
        client (boto3.client): The underlying boto3 SQS client.
    """

    def __init__(self, queue_url: str, region: str = "us-east-1"):
        """Initialise the QueueManager.

        Args:
            queue_url: Full SQS queue URL (from AWS Console).
            region: AWS region string.
        """
        self.queue_url = queue_url
        self.region = region
        # boto3 picks up credentials from the EC2 IAM role automatically
        self.client = boto3.client("sqs", region_name=region)

    def send_message(self, body: dict) -> str:
        """Send a JSON message to the SQS queue.

        Args:
            body: Python dict that will be JSON-serialised as the message body.

        Returns:
            The MessageId assigned by SQS.

        Raises:
            ClientError: If the SQS send operation fails.
        """
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(body),
        )
        return response["MessageId"]

    def receive_messages(self, max_count: int = 10, wait_seconds: int = 5) -> list:
        """Poll the queue for messages.

        Uses long polling (wait_seconds) to reduce empty responses
        and lower API call costs.

        Args:
            max_count: Maximum number of messages to retrieve (1-10).
            wait_seconds: Long-poll wait time in seconds.

        Returns:
            List of message dicts with 'body' (parsed dict) and
            'receipt_handle' fields.
        """
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=min(max_count, 10),
            WaitTimeSeconds=wait_seconds,
        )
        messages = []
        for msg in response.get("Messages", []):
            messages.append({
                "body": json.loads(msg["Body"]),
                "receipt_handle": msg["ReceiptHandle"],
                "message_id": msg["MessageId"],
            })
        return messages

    def delete_message(self, receipt_handle: str) -> bool:
        """Remove a processed message from the queue.

        Must be called after successfully processing a message to
        prevent it from being re-delivered.

        Args:
            receipt_handle: The receipt handle returned by receive_messages.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            return True
        except ClientError:
            return False
