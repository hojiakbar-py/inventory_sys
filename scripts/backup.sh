#!/bin/bash

# Database backup script
set -e

echo "=================================="
echo "Database Backup Script"
echo "=================================="
echo ""

# Create backups directory
mkdir -p ./backups

# Backup filename with timestamp
BACKUP_FILE="./backups/backup_$(date +%Y%m%d_%H%M%S).sql"

# Check if database container is running
if ! docker ps | grep -q "inventory_db"; then
    echo "Error: Database container is not running!"
    exit 1
fi

# Create backup
echo "Creating database backup..."
docker exec inventory_db pg_dump -U inventory_user inventory_db > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ]; then
    echo "✓ Backup created successfully: $BACKUP_FILE"

    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✓ Backup compressed: ${BACKUP_FILE}.gz"

    # Show backup size
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo "  Backup size: $SIZE"
else
    echo "Error: Backup failed!"
    exit 1
fi

# Clean old backups (keep last 7 days)
echo ""
echo "Cleaning old backups (keeping last 7 days)..."
find ./backups -name "backup_*.sql.gz" -mtime +7 -delete
echo "✓ Old backups cleaned"

echo ""
echo "Backup completed successfully!"
