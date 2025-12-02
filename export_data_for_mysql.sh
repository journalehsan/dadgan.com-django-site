#!/usr/bin/env bash
set -euo pipefail

# Export Django data using dumpdata for MySQL migration
# This creates JSON fixtures that can be loaded into any Django-supported database

EXPORT_DIR="./data_export"
EXPORT_FILE="$EXPORT_DIR/django_data.json"

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }

print "Creating export directory..."
mkdir -p "$EXPORT_DIR"

print "Exporting Django data to JSON..."
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  --exclude contenttypes \
  --exclude auth.permission \
  > "$EXPORT_FILE"

if [ $? -eq 0 ]; then
  print "Data exported successfully to: $EXPORT_FILE"
  ls -lh "$EXPORT_FILE"
  print ""
  print "To import this data into MySQL:"
  print "1. Update settings.py to use MySQL database"
  print "2. Run: python manage.py migrate"
  print "3. Run: python manage.py loaddata $EXPORT_FILE"
else
  err "Export failed"
  exit 1
fi
