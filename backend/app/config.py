"""
Application configuration loaded from environment variables.

On EC2, set these in /etc/environment or a .env file.
boto3 uses the EC2 IAM Role for AWS credentials automatically —
no AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY needed.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central config object for all environment-driven settings."""

    # AWS region
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # S3
    S3_BUCKET: str = os.getenv("S3_BUCKET", "cloudshare-files-bucket")

    # DynamoDB
    DYNAMO_FILES_TABLE: str = os.getenv("DYNAMO_FILES_TABLE", "cloudshare-files")
    DYNAMO_NOTIF_TABLE: str = os.getenv("DYNAMO_NOTIF_TABLE", "cloudshare-notifications")

    # SQS
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL", "")

    # SNS
    SNS_TOPIC_ARN: str = os.getenv("SNS_TOPIC_ARN", "")

    # Cognito
    COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID", "")

    # CORS — set to EC2 public IP or domain in production
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


settings = Settings()
