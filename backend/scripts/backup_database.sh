#!/bin/bash
# Database Backup Script

# Load environment variables
source ../venv/bin/activate
export $(cat ../.env | xargs)

# Backup directory
BACKUP_DIR="../backups"
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup filename
DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
MEDIA_BACKUP="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

echo "Starting database backup..."

# PostgreSQL backup
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]; then
    PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > $DB_BACKUP
    echo "PostgreSQL backup created: $DB_BACKUP"

    # Compress backup
    gzip $DB_BACKUP
    echo "Backup compressed: ${DB_BACKUP}.gz"
else
    # SQLite backup
    cp ../db.sqlite3 "$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
    echo "SQLite backup created: $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
fi

# Media files backup
echo "Starting media files backup..."
tar -czf $MEDIA_BACKUP ../media/
echo "Media backup created: $MEDIA_BACKUP"

# Delete old backups (keep last 30 days)
echo "Cleaning old backups..."
find $BACKUP_DIR -name "db_backup_*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "db_backup_*.sqlite3" -mtime +30 -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed successfully!"
echo "Database: ${DB_BACKUP}.gz"
echo "Media: $MEDIA_BACKUP"
