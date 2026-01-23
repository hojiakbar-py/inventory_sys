#!/bin/bash
# ==========================================
# INVENTORY SYSTEM - DATABASE BACKUP SCRIPT
# ==========================================
# Usage: ./backup.sh [daily|weekly|monthly]
#
# This script creates PostgreSQL database backups
# Run with cron for automated backups:
#   0 2 * * * /path/to/backup.sh daily     # Daily at 2 AM
#   0 3 * * 0 /path/to/backup.sh weekly    # Weekly on Sunday at 3 AM
#   0 4 1 * * /path/to/backup.sh monthly   # Monthly on 1st at 4 AM
# ==========================================

set -e

# Configuration
BACKUP_TYPE=${1:-daily}
BACKUP_DIR="/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
RETENTION_DAILY=7
RETENTION_WEEKLY=4
RETENTION_MONTHLY=12

# Database connection (from environment or defaults)
DB_NAME=${DB_NAME:-inventory_db}
DB_USER=${DB_USER:-inventory_user}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

# Create backup directory if not exists
mkdir -p "${BACKUP_DIR}/${BACKUP_TYPE}"

# Backup filename
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_TYPE}/${DB_NAME}_${BACKUP_TYPE}_${DATE}.sql.gz"

echo "=========================================="
echo "Starting ${BACKUP_TYPE} backup at $(date)"
echo "=========================================="

# Create backup
echo "Creating backup: ${BACKUP_FILE}"
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --no-owner \
    --no-acl \
    | gzip > "${BACKUP_FILE}"

# Check if backup was successful
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "Backup created successfully: ${BACKUP_FILE} (${BACKUP_SIZE})"
else
    echo "ERROR: Backup failed!"
    exit 1
fi

# Cleanup old backups based on retention policy
echo "Cleaning up old ${BACKUP_TYPE} backups..."

case ${BACKUP_TYPE} in
    daily)
        RETENTION=${RETENTION_DAILY}
        ;;
    weekly)
        RETENTION=${RETENTION_WEEKLY}
        ;;
    monthly)
        RETENTION=${RETENTION_MONTHLY}
        ;;
    *)
        RETENTION=${RETENTION_DAILY}
        ;;
esac

# Remove backups older than retention period
find "${BACKUP_DIR}/${BACKUP_TYPE}" -name "*.sql.gz" -type f -mtime +${RETENTION} -delete

# Count remaining backups
BACKUP_COUNT=$(find "${BACKUP_DIR}/${BACKUP_TYPE}" -name "*.sql.gz" -type f | wc -l)
echo "Remaining ${BACKUP_TYPE} backups: ${BACKUP_COUNT}"

echo "=========================================="
echo "Backup completed at $(date)"
echo "=========================================="}
