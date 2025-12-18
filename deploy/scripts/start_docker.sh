#!/bin/bash
set -e

LOG_FILE="/home/ubuntu/start_docker.log"
exec > "$LOG_FILE" 2>&1

echo "==== start_docker.sh (ApplicationStart) ===="
date
echo "User: $(whoami)"
echo "Groups: $(groups)"

# Ensure PATH for non-interactive shell
export PATH=/usr/local/bin:/usr/bin:/bin

# Move to app directory (CodeDeploy destination)
cd /home/ubuntu/app || {
  echo "ERROR: /home/ubuntu/app not found"
  exit 1
}

echo "Current directory: $(pwd)"
ls -la

# Ensure required files exist
if [ ! -f compose.yaml ]; then
  echo "ERROR: compose.yaml not found"
  exit 1
fi

if [ ! -f .env ]; then
  echo "ERROR: .env file not found"
  exit 1
fi

# Verify docker access
docker ps >/dev/null 2>&1 || {
  echo "ERROR: docker not accessible by ubuntu user"
  exit 1
}

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region ap-south-1 \
  | docker login --username AWS --password-stdin 957417441966.dkr.ecr.ap-south-1.amazonaws.com

# Pull images defined in compose.yaml
echo "Pulling latest images..."
docker compose pull

# Stop existing containers (safe)
echo "Stopping existing containers..."
docker compose down || true

# Start containers
echo "Starting containers..."
docker compose up -d

# Verify
echo "Running containers:"
docker ps

echo "start_docker.sh completed successfully"
