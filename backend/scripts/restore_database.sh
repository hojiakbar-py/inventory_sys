#!/bin/bash
# Database Restore Script

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: ./restore_database.sh <backup_file>"
    echo "Example: ./restore_database.sh ../backups/db_backup_20240123_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
source ../venv/bin/activate
export $(cat ../.env | xargs)

echo "WARNING: This will overwrite the current database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Starting database restore..."

# Detect backup type and restore
if [[ $BACKUP_FILE == *.sql.gz ]]; then
    # PostgreSQL compressed backup
    echo "Restoring PostgreSQL backup..."
    gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    echo "PostgreSQL restore completed!"

elif [[ $BACKUP_FILE == *.sql ]]; then
    # PostgreSQL uncompressed backup
    echo "Restoring PostgreSQL backup..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME < $BACKUP_FILE
    echo "PostgreSQL restore completed!"

elif [[ $BACKUP_FILE == *.sqlite3 ]]; then
    # SQLite backup
    echo "Restoring SQLite backup..."
    cp $BACKUP_FILE ../db.sqlite3
    echo "SQLite restore completed!"

else
    echo "Error: Unknown backup file format"
    exit 1
fi

echo "Database restored successfully from: $BACKUP_FILE"
