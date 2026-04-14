# cloudshare-lib

A Python library providing OOP wrappers for AWS services used in the Cloud File Sharing application.

## Installation

```bash
pip install cloudshare-lib
```

## Classes

| Class | Service | Purpose |
|---|---|---|
| `StorageManager` | Amazon S3 | Upload, download, delete files |
| `MetadataManager` | Amazon DynamoDB | Store and query file metadata |
| `QueueManager` | Amazon SQS | Async file-share task queue |
| `NotificationManager` | Amazon SNS | Email notifications |
| `CognitoManager` | Amazon Cognito | User auth and JWT tokens |

## Usage

```python
from cloudshare import StorageManager, MetadataManager, QueueManager, NotificationManager, CognitoManager

# S3 file upload
storage = StorageManager(bucket_name="my-files-bucket", region="us-east-1")
storage.upload_file(file_obj, s3_key="users/abc/file.pdf", content_type="application/pdf")
url = storage.generate_presigned_url("users/abc/file.pdf", expiry=3600)

# DynamoDB metadata
db = MetadataManager(table_name="files", pk_name="user_id", sk_name="file_id")
db.put_item({"user_id": "abc", "file_id": "xyz", "filename": "file.pdf"})
items = db.query_items("abc")

# SQS messaging
queue = QueueManager(queue_url="https://sqs.us-east-1.amazonaws.com/123/file-share-queue")
queue.send_message({"action": "share", "file_id": "xyz", "recipient": "user@example.com"})

# SNS notifications
notif = NotificationManager(topic_arn="arn:aws:sns:us-east-1:123:file-notifications")
notif.subscribe_email("user@example.com")
notif.send_file_share_notification("user@example.com", "sharer@example.com", "file.pdf")

# Cognito auth
cognito = CognitoManager(user_pool_id="us-east-1_xxx", client_id="yyy")
cognito.register_user("user@example.com", "Password123!")
tokens = cognito.authenticate_user("user@example.com", "Password123!")
```

## Requirements
- Python 3.10+
- boto3
- EC2 IAM Role with S3, DynamoDB, SQS, SNS, Cognito permissions (no hardcoded credentials needed)

## License
MIT
