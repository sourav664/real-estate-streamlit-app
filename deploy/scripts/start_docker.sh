#!/bin/bash
exec > /home/ubuntu/start_docker.log 2>&1

cd /home/ubuntu/app || exit 1

sudo mkdir -p /var/mlops/audit
sudo chown -R ubuntu:ubuntu /var/mlops/audit

sudo aws ecr get-login-password --region ap-south-1 | sudo docker login --username AWS --password-stdin 957417441966.dkr.ecr.ap-south-1.amazonaws.com

sudo docker pull 957417441966.dkr.ecr.ap-south-1.amazonaws.com/real-estate-streamlit:latest

sudo docker compose down || true
sudo docker compose up -d