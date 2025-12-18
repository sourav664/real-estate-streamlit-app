#!/bin/bash
set -e

LOG_FILE="/home/ubuntu/start_docker.log"
exec > "$LOG_FILE" 2>&1

echo "==== start_docker.sh (ApplicationStart) ===="
date
echo "Running as user: $(whoami)"
echo "Groups: $(groups)"
echo "PWD: $(pwd)"

# Navigate to app directory
cd /home/ubuntu/app || {
    echo "ERROR: Cannot change to /home/ubuntu/app"
    exit 1
}

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Create audit directory with proper ownership
sudo mkdir -p /var/mlops/audit
sudo chown -R ubuntu:ubuntu /var/mlops/audit
echo "Audit directory created and permissions set"

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found in $(pwd)"
    echo "Files in current directory:"
    ls -la
    exit 1
fi
echo ".env file found"

# Check if compose.yaml exists
if [ ! -f compose.yaml ] && [ ! -f docker-compose.yaml ] && [ ! -f docker-compose.yml ]; then
    echo "ERROR: No compose file found"
    echo "Files in current directory:"
    ls -la
    exit 1
fi
echo "Compose file found"

# Wait for docker socket to be accessible
echo "Waiting for Docker socket..."
for i in {1..30}; do
    if docker ps >/dev/null 2>&1; then
        echo "Docker is accessible"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Docker is not accessible after 30 seconds"
        echo "Trying with newgrp docker..."
        exec sg docker -c "$0 $*"
    fi
    echo "Waiting for Docker... attempt $i/30"
    sleep 1
done

# Verify docker works
echo "Testing docker command..."
docker --version || {
    echo "ERROR: docker command failed"
    exit 1
}

echo "Checking docker daemon..."
docker ps || {
    echo "ERROR: Cannot connect to docker daemon"
    echo "Retrying with newgrp..."
    exec sg docker -c "$0 $*"
}

# ECR login
echo "Logging into ECR..."
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 957417441966.dkr.ecr.ap-south-1.amazonaws.com || {
    echo "ERROR: ECR login failed"
    exit 1
}

# Pull latest image
echo "Pulling latest image..."
docker pull 957417441966.dkr.ecr.ap-south-1.amazonaws.com/real-estate-streamlit:latest || {
    echo "ERROR: Docker pull failed"
    exit 1
}

# Stop and remove old containers
echo "Stopping old containers..."
docker compose down 2>&1 || echo "No existing containers to stop"

# Start new containers
echo "Starting new containers..."
docker compose up -d || {
    echo "ERROR: docker compose up failed"
    exit 1
}

# Verify container is running
echo "Waiting for container to start..."
sleep 5

echo "Checking running containers..."
docker ps

if docker ps | grep -q real-estate; then
    echo "SUCCESS: Container is running"
else
    echo "WARNING: Container may not be running"
    echo "Container logs:"
    docker logs real-estate 2>&1 || echo "Could not fetch logs"
fi

echo "start_docker.sh completed successfully"