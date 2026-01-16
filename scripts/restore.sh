#!/bin/bash

# Database restore script
set -e

echo "=================================="
echo "Database Restore Script"
echo "=================================="
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Check if database container is running
if ! docker ps | grep -q "inventory_db"; then
    echo "Error: Database container is not running!"
    echo "Please start the containers first: docker-compose up -d"
    exit 1
fi

# Confirmation
echo "WARNING: This will replace the current database with the backup!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Extract if compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Extracting backup file..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    SQL_FILE="$TEMP_FILE"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Restore database
echo "Restoring database..."
cat "$SQL_FILE" | docker exec -i inventory_db psql -U inventory_user -d inventory_db

# Clean up temporary file
if [ "$SQL_FILE" != "$BACKUP_FILE" ]; then
    rm "$SQL_FILE"
fi

echo ""
echo "✓ Database restored successfully!"
echo ""
echo "You may need to restart the backend container:"
echo "  docker-compose restart backend"
