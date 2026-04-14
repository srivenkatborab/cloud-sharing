"""
cloudshare: A Python library for AWS cloud file sharing operations.

Provides OOP wrappers for S3, DynamoDB, SQS, SNS, and Cognito
to support the Cloud File Sharing application.
"""

from .storage import StorageManager
from .database import MetadataManager
from .messaging import QueueManager
from .notifications import NotificationManager
from .auth import CognitoManager

__version__ = "0.1.0"
__all__ = [
    "StorageManager",
    "MetadataManager",
    "QueueManager",
    "NotificationManager",
    "CognitoManager",
]
