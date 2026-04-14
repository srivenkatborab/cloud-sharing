"""
NotificationManager: OOP wrapper for Amazon SNS operations.

Handles email subscriptions and publishing notifications
when files are shared between users.
"""

import boto3
from botocore.exceptions import ClientError


class NotificationManager:
    """Manages push notifications using Amazon SNS.

    Supports subscribing user emails to a topic and publishing
    file-share notification messages.

    Attributes:
        topic_arn (str): The SNS topic ARN.
        region (str): AWS region of the SNS topic.
        client (boto3.client): The underlying boto3 SNS client.
    """

    def __init__(self, topic_arn: str, region: str = "us-east-1"):
        """Initialise the NotificationManager.

        Args:
            topic_arn: Full SNS topic ARN (from AWS Console).
            region: AWS region string.
        """
        self.topic_arn = topic_arn
        self.region = region
        # boto3 picks up credentials from the EC2 IAM role automatically
        self.client = boto3.client("sns", region_name=region)

    def subscribe_email(self, email: str) -> str:
        """Subscribe an email address to the SNS topic.

        The subscriber will receive a confirmation email from AWS.
        Notifications are only delivered after the subscription is confirmed.

        Args:
            email: The recipient's email address.

        Returns:
            The SubscriptionArn (will be 'pending confirmation' until confirmed).

        Raises:
            ClientError: If the subscription request fails.
        """
        response = self.client.subscribe(
            TopicArn=self.topic_arn,
            Protocol="email",
            Endpoint=email,
            ReturnSubscriptionArn=True,
        )
        return response["SubscriptionArn"]

    def publish(self, subject: str, message: str) -> str:
        """Publish a raw message to the SNS topic.

        Args:
            subject: Email subject line (max 100 characters).
            message: Message body text.

        Returns:
            The MessageId assigned by SNS.

        Raises:
            ClientError: If the publish operation fails.
        """
        response = self.client.publish(
            TopicArn=self.topic_arn,
            Subject=subject,
            Message=message,
        )
        return response["MessageId"]

    def send_file_share_notification(
        self, recipient_email: str, sharer_email: str, filename: str
    ) -> str:
        """Send a formatted file-share notification email via SNS.

        Publishes a human-readable notification message to the topic.
        The recipient must already be subscribed.

        Args:
            recipient_email: Email of the user receiving the shared file.
            sharer_email: Email of the user who shared the file.
            filename: Name of the shared file.

        Returns:
            The MessageId assigned by SNS.
        """
        subject = f"CloudShare: {sharer_email} shared a file with you"
        message = (
            f"Hello,\n\n"
            f"{sharer_email} has shared the file '{filename}' with you "
            f"on CloudShare.\n\n"
            f"Log in to your account to view and download the file.\n\n"
            f"-- The CloudShare Team"
        )
        return self.publish(subject=subject, message=message)
