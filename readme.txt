================================================================================
CloudShare — Cloud-Based File Sharing System
NCI MSc Cloud Computing — Cloud Platform Programming CA
================================================================================

PROJECT OVERVIEW
----------------
A cloud-native file sharing web application built on AWS.
Backend: Python (FastAPI) | Frontend: Next.js (TypeScript, Tailwind CSS)
Deployed on: Amazon EC2 with Nginx reverse proxy

AWS SERVICES USED (5)
---------------------
1. Amazon S3         — Secure file object storage
2. Amazon DynamoDB   — File metadata and notifications (NoSQL)
3. Amazon SQS        — Async queue for file-share processing
4. Amazon SNS        — Email notifications on file share
5. Amazon Cognito    — User registration, login, JWT authentication

CUSTOM LIBRARY
--------------
Package: cloudshare-lib
PyPI URL: https://pypi.org/project/cloudshare-lib/
Location: cloudshare-lib/

Classes:
  StorageManager   (cloudshare/storage.py)      — S3 operations
  MetadataManager  (cloudshare/database.py)     — DynamoDB CRUD
  QueueManager     (cloudshare/messaging.py)    — SQS send/receive
  NotificationManager (cloudshare/notifications.py) — SNS email
  CognitoManager   (cloudshare/auth.py)         — Cognito auth

PROJECT STRUCTURE
-----------------
cloud-sharing-2/
├── cloudshare-lib/          Custom Python library (published to PyPI)
│   ├── cloudshare/
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── database.py
│   │   ├── messaging.py
│   │   ├── notifications.py
│   │   └── auth.py
│   ├── pyproject.toml
│   └── README.md
├── backend/                 FastAPI backend
│   ├── app/
│   │   ├── main.py          FastAPI app + lifespan
│   │   ├── config.py        Environment config
│   │   ├── middleware/
│   │   │   └── auth.py      Cognito JWT verification
│   │   ├── routes/
│   │   │   ├── auth.py      /api/auth/*
│   │   │   ├── files.py     /api/files/*
│   │   │   ├── share.py     /api/share/*
│   │   │   └── notifications.py  /api/notifications/*
│   │   └── workers/
│   │       └── share_worker.py   SQS background worker
│   ├── requirements.txt
│   └── .env.example
├── frontend/                Next.js frontend
│   ├── app/
│   │   ├── page.tsx         Public dashboard
│   │   ├── register/        Registration
│   │   ├── confirm/         Email confirmation
│   │   ├── login/           Login
│   │   ├── dashboard/       File manager (protected)
│   │   ├── upload/          File upload (protected)
│   │   └── notifications/   Notifications (protected)
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── FileCard.tsx
│   └── lib/
│       ├── api.ts           Axios client with auth
│       └── auth.ts          Token helpers
├── nginx/nginx.conf         Reverse proxy config
├── deploy/
│   ├── setup.sh             EC2 bootstrap script
│   └── aws-resources-setup.md  Step-by-step AWS Console setup
└── readme.txt               This file

DEPENDENCIES
------------
Backend (Python):
  fastapi==0.111.0
  uvicorn[standard]==0.29.0
  boto3==1.34.84
  cloudshare-lib==0.1.0
  python-jose[cryptography]==3.3.0
  python-multipart==0.0.9
  python-dotenv==1.0.1
  pydantic[email]==2.7.1

Frontend (Node):
  next@14.2.3
  react@^18
  axios@^1.7.2
  tailwindcss@^3.4.3
  lucide-react@^0.378.0
  typescript@^5

DEPLOYMENT STEPS
----------------
1. Create AWS resources via the Console (see deploy/aws-resources-setup.md)
2. Launch EC2 (Ubuntu 22.04, t2.small) with IAM Role:
     AmazonS3FullAccess, AmazonDynamoDBFullAccess, AmazonSQSFullAccess,
     AmazonSNSFullAccess, AmazonCognitoPowerUser
3. Assign Elastic IP to the EC2 instance
4. SSH into the instance
5. Clone this repository
6. Edit /etc/environment with your AWS resource values (see backend/.env.example)
7. Run: chmod +x deploy/setup.sh && sudo deploy/setup.sh
8. Access the app at: http://YOUR_ELASTIC_IP

PUBLISH LIBRARY TO PYPI (before setup.sh)
------------------------------------------
  cd cloudshare-lib
  pip install build twine
  python -m build
  twine upload dist/*
  # Enter your PyPI username and password/token when prompted

ENVIRONMENT VARIABLES (set in /etc/environment on EC2)
-------------------------------------------------------
  AWS_REGION              e.g. us-east-1
  S3_BUCKET               S3 bucket name
  DYNAMO_FILES_TABLE      DynamoDB table for file metadata
  DYNAMO_NOTIF_TABLE      DynamoDB table for notifications
  SQS_QUEUE_URL           Full SQS queue URL
  SNS_TOPIC_ARN           Full SNS topic ARN
  COGNITO_USER_POOL_ID    Cognito User Pool ID
  COGNITO_CLIENT_ID       Cognito App Client ID
  CORS_ORIGINS            Frontend URL (http://YOUR_ELASTIC_IP)

NOTE: No AWS access keys are needed in the environment.
boto3 uses the EC2 IAM Role for credentials automatically.

API ENDPOINTS
-------------
Public:
  GET  /api/health           Health check

Auth (no token required):
  POST /api/auth/register    Register user
  POST /api/auth/confirm     Confirm email
  POST /api/auth/login       Login → returns JWT tokens

Protected (Bearer token required):
  GET  /api/auth/me          Get current user profile
  GET  /api/files/           List user's files
  POST /api/files/upload     Upload file (multipart)
  GET  /api/files/{id}/download  Get presigned download URL
  DEL  /api/files/{id}       Delete file
  POST /api/share/           Share file → queues SQS message
  GET  /api/notifications/   List notifications
  PATCH /api/notifications/{id}/read  Mark notification read

CONTACT / VERSION CONTROL
--------------------------
Private GitHub repository used for version control throughout development.
Repository: https://github.com/yourusername/cloud-sharing-2 (private)
================================================================================
