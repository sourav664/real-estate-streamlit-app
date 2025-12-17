#!/bin/bash
set -e

LOG_FILE="/home/ubuntu/setup_backup.log"
exec > "$LOG_FILE" 2>&1

echo "==== setup_backup.sh (AfterInstall) ===="
date
echo "Running as user: $(whoami)"
echo "PWD: $(pwd)"

# Ensure audit directory exists
mkdir -p /var/mlops/audit

# Find aws CLI
AWS_BIN="$(command -v aws || true)"
if [ -z "$AWS_BIN" ]; then
  echo "ERROR: aws CLI not found in PATH; install awscli for ubuntu or fix PATH"
  exit 1
fi
"$AWS_BIN" --version || echo "Warning: aws --version failed"

# Build cron line with full path and its own logging
CRON_JOB="0 2 * * * $AWS_BIN s3 sync /var/mlops/audit s3://mlops-audit-backups/audit >> /home/ubuntu/s3_sync.log 2>&1"

# Load existing crontab (do not let failure kill script)
crontab -l 2>/dev/null > /tmp/current_cron || true

# Append job if missing
if ! grep -Fxq "$CRON_JOB" /tmp/current_cron; then
    echo "$CRON_JOB" >> /tmp/current_cron
    if crontab /tmp/current_cron; then
        echo "Cron job added."
    else
        echo "ERROR: failed to install crontab for ubuntu"
        exit 1
    fi
else
    echo "Cron job already exists."
fi

rm -f /tmp/current_cron

echo "S3 backup cron job setup completed."
