#!/bin/bash
# Database Backup Script for Welcome Link
# Run daily via cron: 0 2 * * * /path/to/backup.sh

set -e

# Configuration
BACKUP_DIR="/var/backups/welcome-link"
DB_PATH="/app/app.db"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/welcome_link_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp "$DB_PATH" "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
echo "Compressed: ${BACKUP_FILE}.gz"

# Calculate size
SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
echo "Backup size: $SIZE"

# Clean old backups
echo "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "welcome_link_*.db.gz" -type f -mtime +$RETENTION_DAYS -delete

# List current backups
echo "Current backups:"
ls -lh "$BACKUP_DIR"/*.db.gz 2>/dev/null | tail -5

# Optional: Upload to S3
# aws s3 cp "${BACKUP_FILE}.gz" s3://your-bucket/backups/

# Optional: Send notification
# curl -X POST "https://api.example.com/notify" -d "Backup completed: $SIZE"

echo "Backup completed successfully!"