# AWS Resource Setup Guide
# (Amazon Student Account — AWS Console Only, No Local CLI Required)

Complete these steps in the AWS Management Console BEFORE running setup.sh.

---

## 1. Amazon S3 — File Storage

1. Go to **S3 > Create bucket**
2. Bucket name: `cloudshare-files-bucket` (must be globally unique — add your initials)
3. Region: `us-east-1`
4. Keep **Block all public access** ON (files accessed via presigned URLs only)
5. Click **Create bucket**

---

## 2. Amazon DynamoDB — Metadata Tables

Create TWO tables:

**Table 1: `cloudshare-files`**
- Partition key: `user_id` (String)
- Sort key: `file_id` (String)
- Billing: On-demand

**Table 2: `cloudshare-notifications`**
- Partition key: `recipient_email` (String)
- Sort key: `notification_id` (String)
- Billing: On-demand

---

## 3. Amazon SQS — Share Queue

1. Go to **SQS > Create queue**
2. Type: **Standard**
3. Name: `file-share-queue`
4. Default settings are fine
5. Copy the **Queue URL** (needed for .env)

---

## 4. Amazon SNS — Notifications

1. Go to **SNS > Topics > Create topic**
2. Type: **Standard**
3. Name: `file-notifications`
4. Copy the **Topic ARN** (needed for .env)

---

## 5. Amazon Cognito — User Authentication

1. Go to **Cognito > User pools > Create user pool**
2. Sign-in: **Email** only
3. Password policy: Minimum 8 chars, upper + lower + number + symbol
4. MFA: **No MFA** (simplest for demo)
5. Email verification: **Cognito** (sends code via Cognito's email)
6. App client:
   - Type: **Public client** (no secret)
   - Name: `cloudshare-app`
   - Auth flows: enable **USER_PASSWORD_AUTH**
7. Copy **User Pool ID** and **App Client ID**

---

## 6. EC2 — Instance with IAM Role

1. Launch EC2 > **Ubuntu 22.04**, **t2.small** (or t2.micro)
2. Key pair: create or use existing `.pem` file
3. Security group — allow inbound:
   - Port 22 (SSH) from your IP
   - Port 80 (HTTP) from 0.0.0.0/0
4. **IAM Instance Profile** (Advanced > IAM instance profile):
   - Create a new role: `EC2-CloudShare-Role`
   - Attach policies:
     - `AmazonS3FullAccess`
     - `AmazonDynamoDBFullAccess`
     - `AmazonSQSFullAccess`
     - `AmazonSNSFullAccess`
     - `AmazonCognitoPowerUser`
5. Assign an **Elastic IP** for a stable public URL

---

## 7. Set Environment Variables on EC2

SSH into the EC2 instance and edit `/etc/environment`:

```bash
sudo nano /etc/environment
```

Add (replace values with your actual ARNs/IDs):

```
AWS_REGION="us-east-1"
S3_BUCKET="cloudshare-files-bucket-yourname"
DYNAMO_FILES_TABLE="cloudshare-files"
DYNAMO_NOTIF_TABLE="cloudshare-notifications"
SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT_ID/file-share-queue"
SNS_TOPIC_ARN="arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:file-notifications"
COGNITO_USER_POOL_ID="us-east-1_XXXXXXXXX"
COGNITO_CLIENT_ID="XXXXXXXXXXXXXXXXXXXXXXXXXX"
CORS_ORIGINS="http://YOUR_ELASTIC_IP"
```

Then reload: `source /etc/environment`

---

## 8. Clone Repo & Run Setup

```bash
cd /home/ubuntu
git clone https://github.com/yourusername/cloud-sharing-2.git
chmod +x cloud-sharing-2/deploy/setup.sh
sudo cloud-sharing-2/deploy/setup.sh
```

Your app is now live at: `http://YOUR_ELASTIC_IP`
