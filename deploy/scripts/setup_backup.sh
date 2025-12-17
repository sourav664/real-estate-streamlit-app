#!/bin/bash
set -e

echo "Setting up S3 backup cron job..."

AUDIT_DIR="/var/mlops/audit"
S3_BUCKET="s3://mlops-audit-backups/audit"
LOG_FILE="/var/log/mlops_s3_backup.log"

# Ensure audit directory exists
mkdir -p $AUDIT_DIR

# Full path to aws (important for cron)
AWS_BIN="/usr/local/bin/aws"

CRON_JOB="*/10 * * * * $AWS_BIN s3 sync $AUDIT_DIR $S3_BUCKET >> $LOG_FILE 2>&1"


# Add cron job if not already present
(crontab -l 2>/dev/null | grep -F "$S3_BUCKET") || \
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "S3 backup cron job configured."
