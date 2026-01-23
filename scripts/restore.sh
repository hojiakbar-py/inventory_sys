#!/bin/bash
# ==========================================
# INVENTORY SYSTEM - DATABASE RESTORE SCRIPT
# ==========================================
# Usage: ./restore.sh <backup_file.sql.gz>
#
# This script restores PostgreSQL database from backup
# ==========================================

set -e

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    find /backups -name "*.sql.gz" -type f | sort -r | head -10
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Database connection (from environment or defaults)
DB_NAME=${DB_NAME:-inventory_db}
DB_USER=${DB_USER:-inventory_user}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "=========================================="
echo "WARNING: This will overwrite the current database!"
echo "Database: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo "=========================================="
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Starting restore at $(date)"
echo ""

# Drop and recreate database
echo "Recreating database..."
PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS ${DB_NAME};"

PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "CREATE DATABASE ${DB_NAME};"

# Restore from backup
echo "Restoring from backup..."
gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}"

echo ""
echo "=========================================="
echo "Restore completed at $(date)"
echo "=========================================="
echo ""
echo "Don't forget to run migrations if needed:"
echo "  docker-compose exec backend python manage.py migrate"
