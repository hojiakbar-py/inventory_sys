@echo off
REM Database Backup Script for Windows

REM Timestamp
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Backup directory
set BACKUP_DIR=..\backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Starting database backup...

REM SQLite backup (default for development)
if exist ..\db.sqlite3 (
    copy ..\db.sqlite3 "%BACKUP_DIR%\db_backup_%TIMESTAMP%.sqlite3"
    echo SQLite backup created: %BACKUP_DIR%\db_backup_%TIMESTAMP%.sqlite3
)

REM Media files backup
echo Starting media files backup...
powershell Compress-Archive -Path ..\media\* -DestinationPath "%BACKUP_DIR%\media_backup_%TIMESTAMP%.zip" -Force
echo Media backup created: %BACKUP_DIR%\media_backup_%TIMESTAMP%.zip

REM Delete old backups (older than 30 days)
echo Cleaning old backups...
forfiles /p "%BACKUP_DIR%" /s /m db_backup_*.sqlite3 /d -30 /c "cmd /c del @path" 2>nul
forfiles /p "%BACKUP_DIR%" /s /m media_backup_*.zip /d -30 /c "cmd /c del @path" 2>nul

echo Backup completed successfully!
pause
