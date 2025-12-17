#!/bin/bash
set -e

LOG="/home/ubuntu/setup_backup.log"
exec > "$LOG" 2>&1

echo "Starting setup_backup.sh"

# Ensure PATH for aws
export PATH=/usr/local/bin:/usr/bin:/bin

# Ensure audit directory exists (host directory)
mkdir -p /var/mlops/audit
chmod -R 777 /var/mlops/audit

CRON_JOB="0 2 * * * /usr/local/bin/aws s3 sync /var/mlops/audit s3://mlops-audit-backups/audit"

# Load existing cron safely
crontab -l 2>/dev/null > /tmp/cron || true

if ! grep -Fxq "$CRON_JOB" /tmp/cron; then
  echo "$CRON_JOB" >> /tmp/cron
  crontab /tmp/cron
  echo "Cron job added"
else
  echo "Cron job already exists"
fi

rm -f /tmp/cron

echo "setup_backup.sh completed successfully"
