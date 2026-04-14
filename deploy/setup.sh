#!/bin/bash
# =============================================================================
# CloudShare EC2 Setup Script
# =============================================================================
# Run this ONCE on a fresh Ubuntu 22.04/24.04 EC2 instance after cloning the repo.
# Before running:
#   1. Fill in /etc/environment with the AWS resource values (see .env.example)
#   2. Ensure the EC2 instance has an IAM Role attached with:
#      AmazonS3FullAccess, AmazonDynamoDBFullAccess, AmazonSQSFullAccess,
#      AmazonSNSFullAccess, AmazonCognitoPowerUser
#
# Usage:
#   chmod +x deploy/setup.sh
#   sudo deploy/setup.sh
# =============================================================================

set -e  # Exit immediately on any error

echo "=== [1/6] Updating system packages ==="
apt-get update -y
apt-get upgrade -y

echo "=== [2/6] Installing Python 3.12, pip, Node 20, npm, nginx ==="
# Ubuntu 24.04 (Noble) ships python3.12 — python3.11 is not in its repos.
apt-get install -y python3.12 python3.12-venv python3-pip nginx curl

# Install Node.js 20 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install PM2 to keep processes alive after SSH disconnects
npm install -g pm2

echo "=== [3/6] Installing Python backend dependencies ==="
cd /home/ubuntu/cloud-sharing-2

# cloudshare-lib is a local library bundled in this repo (not on public PyPI).
# Install it directly from the pre-built wheel.
# Ubuntu 24.04 enforces PEP 668 — use --break-system-packages for system-wide installs
# (or use a venv, but PM2 needs the system python path)
pip3 install --break-system-packages cloudshare-lib/dist/cloudshare_lib-0.1.0-py3-none-any.whl

# Install backend requirements (cloudshare-lib is already installed above)
pip3 install --break-system-packages -r backend/requirements.txt

echo "=== [4/6] Building Next.js frontend ==="
cd /home/ubuntu/cloud-sharing-2/frontend
npm install
npm run build

echo "=== [5/6] Configuring Nginx ==="
cp /home/ubuntu/cloud-sharing-2/nginx/nginx.conf /etc/nginx/sites-available/default
nginx -t  # Test config before applying
systemctl restart nginx
systemctl enable nginx

echo "=== [6/6] Starting application processes with PM2 ==="
cd /home/ubuntu/cloud-sharing-2

# Start FastAPI backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" \
  --name cloudshare-api \
  --cwd /home/ubuntu/cloud-sharing-2/backend

# Start Next.js frontend
pm2 start "npm start" \
  --name cloudshare-frontend \
  --cwd /home/ubuntu/cloud-sharing-2/frontend

# Save PM2 process list so it restarts on reboot
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu

echo ""
echo "=== Setup complete! ==="
echo "Backend API:  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/health"
echo "Frontend:     http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "To view logs: pm2 logs"
echo "To restart:   pm2 restart all"
