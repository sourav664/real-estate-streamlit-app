#!/bin/bash
exec > /home/ubuntu/start_docker.log 2>&1

cd /home/ubuntu/app || exit 1

mkdir -p /var/mlops/audit
chmod -R 777 /var/mlops/audit

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 957417441966.dkr.ecr.ap-south-1.amazonaws.com

docker pull 957417441966.dkr.ecr.ap-south-1.amazonaws.com/real-estate-streamlit:latest

docker compose down || true
docker compose up -d
