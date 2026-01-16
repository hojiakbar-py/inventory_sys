#!/usr/bin/env python
"""
Script to migrate data from SQLite to PostgreSQL
Usage: python migrate_to_postgresql.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.core.management import call_command
from django.db import connections
from decouple import config

def migrate_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""

    print("=" * 50)
    print("SQLite to PostgreSQL Migration")
    print("=" * 50)

    # Check if PostgreSQL is configured
    db_engine = config('DB_ENGINE', default='django.db.backends.sqlite3')

    if 'postgresql' not in db_engine:
        print("Error: PostgreSQL is not configured in .env file")
        print("Please update DB_ENGINE to django.db.backends.postgresql")
        sys.exit(1)

    # Check SQLite database exists
    sqlite_db = 'db.sqlite3'
    if not os.path.exists(sqlite_db):
        print(f"Error: SQLite database not found: {sqlite_db}")
        sys.exit(1)

    print(f"\n✓ SQLite database found: {sqlite_db}")

    # Test PostgreSQL connection
    try:
        conn = connections['default']
        conn.ensure_connection()
        print(f"✓ PostgreSQL connection successful")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

    # Backup directory
    backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    print("\n" + "=" * 50)
    print("Step 1: Creating data dump from SQLite")
    print("=" * 50)

    dump_file = os.path.join(backup_dir, 'sqlite_data_dump.json')

    try:
        # Export data from SQLite
        with open(dump_file, 'w') as f:
            call_command('dumpdata',
                        '--natural-foreign',
                        '--natural-primary',
                        '--exclude=contenttypes',
                        '--exclude=auth.permission',
                        stdout=f)
        print(f"✓ Data exported to: {dump_file}")
    except Exception as e:
        print(f"Error exporting data: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Step 2: Setting up PostgreSQL database")
    print("=" * 50)

    try:
        # Run migrations on PostgreSQL
        print("Running migrations...")
        call_command('migrate', '--run-syncdb')
        print("✓ Migrations completed")
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Step 3: Importing data to PostgreSQL")
    print("=" * 50)

    try:
        # Import data to PostgreSQL
        call_command('loaddata', dump_file)
        print("✓ Data imported successfully")
    except Exception as e:
        print(f"Error importing data: {e}")
        print("\nYou can try importing manually:")
        print(f"python manage.py loaddata {dump_file}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Migration completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Test your application with PostgreSQL")
    print("2. Backup your SQLite database: cp db.sqlite3 db.sqlite3.backup")
    print("3. Update your production settings")
    print(f"\nData dump saved at: {dump_file}")


if __name__ == '__main__':
    response = input("\nThis will migrate data from SQLite to PostgreSQL.\nContinue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_to_postgresql()
    else:
        print("Migration cancelled.")
