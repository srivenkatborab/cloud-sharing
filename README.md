# CloudShare — Cloud-Based File Sharing System

A cloud-native file sharing web application built on AWS.  
**Backend:** Python (FastAPI) | **Frontend:** Next.js (TypeScript, Tailwind CSS)  
**Deployed on:** Amazon EC2 with Nginx reverse proxy

---

## AWS Services

| Service | Purpose |
|---|---|
| **Amazon S3** | Secure file object storage |
| **Amazon DynamoDB** | File metadata and notifications (NoSQL) |
| **Amazon SQS** | Async queue for file-share processing |
| **Amazon SNS** | Email notifications on file share |
| **Amazon Cognito** | User registration, login, JWT authentication |

---

## Project Structure

```
cloud-sharing-2/
├── cloudshare-lib/          # Custom Python library (published to PyPI)
│   ├── cloudshare/
│   │   ├── storage.py       # StorageManager — S3 operations
│   │   ├── database.py      # MetadataManager — DynamoDB CRUD
│   │   ├── messaging.py     # QueueManager — SQS send/receive
│   │   ├── notifications.py # NotificationManager — SNS email
│   │   └── auth.py          # CognitoManager — Cognito auth
│   ├── pyproject.toml
│   └── README.md
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point + lifespan
│   │   ├── config.py        # Environment config (reads from .env)
│   │   ├── middleware/
│   │   │   └── auth.py      # Cognito JWT verification middleware
│   │   ├── routes/
│   │   │   ├── auth.py      # POST /api/auth/* (register, confirm, login)
│   │   │   ├── files.py     # GET/POST/DEL /api/files/*
│   │   │   ├── share.py     # POST /api/share/ (enqueues SQS message)
│   │   │   └── notifications.py  # GET/PATCH /api/notifications/*
│   │   └── workers/
│   │       └── share_worker.py   # Background SQS consumer
│   ├── requirements.txt
│   └── .env.example         # Template for required environment variables
├── frontend/                # Next.js 14 frontend
│   ├── app/
│   │   ├── page.tsx         # Landing / public dashboard
│   │   ├── register/        # User registration page
│   │   ├── confirm/         # Email confirmation page
│   │   ├── login/           # Login page
│   │   ├── dashboard/       # File manager (protected)
│   │   ├── upload/          # File upload (protected)
│   │   └── notifications/   # Notifications (protected)
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── FileCard.tsx
│   └── lib/
│       ├── api.ts            # Axios client with auth header injection
│       └── auth.ts           # Token helpers (localStorage)
├── nginx/
│   └── nginx.conf            # Reverse proxy: port 80 → backend :8000 / frontend :3000
├── deploy/
│   ├── setup.sh              # EC2 bootstrap (install deps, start services)
│   └── aws-resources-setup.md  # Step-by-step AWS Console resource creation
├── .gitignore
└── README.md
```

---

## Quick Start (Local Dev)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Fill in your AWS resource values
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
pnpm install                   # or npm install
pnpm dev                       # runs on http://localhost:3000
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the values.  
On EC2, add these to `/etc/environment` instead.

| Variable | Description |
|---|---|
| `AWS_REGION` | e.g. `us-east-1` |
| `S3_BUCKET` | S3 bucket name |
| `DYNAMO_FILES_TABLE` | DynamoDB table for file metadata |
| `DYNAMO_NOTIF_TABLE` | DynamoDB table for notifications |
| `SQS_QUEUE_URL` | Full SQS queue URL |
| `SNS_TOPIC_ARN` | Full SNS topic ARN |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | Cognito App Client ID |
| `CORS_ORIGINS` | Frontend URL (e.g. `http://YOUR_ELASTIC_IP`) |

> No AWS access keys are needed. `boto3` uses the EC2 IAM Role automatically.

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | — | Health check |
| `POST` | `/api/auth/register` | — | Register user |
| `POST` | `/api/auth/confirm` | — | Confirm email |
| `POST` | `/api/auth/login` | — | Login → returns JWT tokens |
| `GET` | `/api/auth/me` | Bearer | Get current user profile |
| `GET` | `/api/files/` | Bearer | List user's files |
| `POST` | `/api/files/upload` | Bearer | Upload file (multipart) |
| `GET` | `/api/files/{id}/download` | Bearer | Get presigned download URL |
| `DELETE` | `/api/files/{id}` | Bearer | Delete file |
| `POST` | `/api/share/` | Bearer | Share file → queues SQS message |
| `GET` | `/api/notifications/` | Bearer | List notifications |
| `PATCH` | `/api/notifications/{id}/read` | Bearer | Mark notification as read |

---

## Custom Library — `cloudshare-lib`

Published to PyPI: [`cloudshare-lib`](https://pypi.org/project/cloudshare-lib/)

```bash
pip install cloudshare-lib
```

Provides OOP wrappers for all five AWS services. See [`cloudshare-lib/README.md`](cloudshare-lib/README.md) for full usage examples.

---

## Deployment (EC2)

1. Create AWS resources — follow [`deploy/aws-resources-setup.md`](deploy/aws-resources-setup.md)
2. Launch EC2 (Ubuntu 22.04, `t2.small`) with IAM Role:  
   `AmazonS3FullAccess`, `AmazonDynamoDBFullAccess`, `AmazonSQSFullAccess`, `AmazonSNSFullAccess`, `AmazonCognitoPowerUser`
3. Assign an Elastic IP to the instance
4. SSH in, clone this repo, set `/etc/environment` with the variables above
5. Run:
   ```bash
   chmod +x deploy/setup.sh && sudo deploy/setup.sh
   ```
6. Access the app at `http://YOUR_ELASTIC_IP`

### Publish Library to PyPI (before running setup.sh)

```bash
cd cloudshare-lib
pip install build twine
python -m build
twine upload dist/*
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Axios |
| Auth | Amazon Cognito (JWT) |
| Storage | Amazon S3 |
| Database | Amazon DynamoDB |
| Messaging | Amazon SQS + SNS |
| Proxy | Nginx |
| Hosting | Amazon EC2 (Ubuntu 22.04) |
