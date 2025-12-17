#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

apt-get update -y

# Docker
apt-get install -y docker.io
systemctl start docker
systemctl enable docker

# Utilities
apt-get install -y unzip curl cron
systemctl start cron
systemctl enable cron

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip -o /tmp/awscliv2.zip -d /tmp/
./tmp/aws/install

# Docker permission
usermod -aG docker ubuntu

echo "Dependencies installed successfully."