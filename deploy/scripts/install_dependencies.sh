#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "Updating system..."
apt-get update -y

echo "Installing required packages..."
apt-get install -y \
  docker.io \
  docker-compose-plugin \
  unzip \
  curl \
  cron


echo "Starting services..."
systemctl start docker
systemctl enable docker
systemctl start cron
systemctl enable cron

# Install AWS CLI only if not installed
if ! command -v aws >/dev/null 2>&1; then
  echo "Installing AWS CLI..."
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
  unzip -o /tmp/awscliv2.zip -d /tmp
  /tmp/aws/install
  rm -rf /tmp/awscliv2.zip /tmp/aws
else
  echo "AWS CLI already installed, skipping."
fi

echo "Adding ubuntu user to docker group..."
usermod -aG docker ubuntu

echo "Creating audit directory..."
mkdir -p /var/mlops/audit
chown -R ubuntu:ubuntu /var/mlops/audit
chmod 755 /var/mlops/audit


# CRITICAL: Refresh docker group membership for existing processes
echo "Refreshing docker group..."
newgrp docker || true

# Ensure docker socket has correct permissions
chmod 666 /var/run/docker.sock

# Verify ubuntu user can access docker
echo "Verifying docker access for ubuntu user..."
su - ubuntu -c "docker ps" || {
    echo "WARNING: ubuntu user cannot access docker yet, but should work after relogin"
}

echo "install_dependencies.sh completed successfully"