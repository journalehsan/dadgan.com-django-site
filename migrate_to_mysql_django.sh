#!/usr/bin/env bash
set -euo pipefail

# Complete migration from local SQLite to remote MySQL using Django's native tools
# This approach is more reliable than raw SQL conversion

### Config ###
REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PORT=22
REMOTE_PASS='Trk@#1403'

DB_CONTAINER="docker-mariadb-phpmyadmin-mariadb-1"
REMOTE_DB_NAME="dadgan_django"
REMOTE_DB_USER="root"
REMOTE_DB_PASS="my-secret-pw"

EXPORT_DIR="./data_export"
EXPORT_FILE="$EXPORT_DIR/django_data.json"
### End config ###

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }

usage() {
  cat <<EOF
Usage: $0

This script:
1. Exports data from local SQLite using Django's dumpdata
2. Creates MySQL database on remote server
3. Uploads the data file
4. Provides instructions for importing (requires Django app access on remote)

EOF
}

if [ "$#" -gt 0 ] && [ "$1" = "--help" ]; then
  usage
  exit 0
fi

print "Step 1: Exporting local Django data..."
mkdir -p "$EXPORT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
  print "Activating virtual environment..."
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

if ! python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions \
  > "$EXPORT_FILE"; then
  err "Django dumpdata failed. Is your Django environment configured?"
  exit 1
fi

print "✓ Data exported to: $EXPORT_FILE"
ls -lh "$EXPORT_FILE"

if ! command -v sshpass >/dev/null 2>&1; then
  err "sshpass is required. Install and re-run."
  exit 1
fi

print ""
print "Step 2: Creating MySQL database on remote server..."

sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
if docker inspect $DB_CONTAINER >/dev/null 2>&1; then
  echo \"Creating database ${REMOTE_DB_NAME}...\"
  docker exec $DB_CONTAINER mariadb -u${REMOTE_DB_USER} -p${REMOTE_DB_PASS} -e \"CREATE DATABASE IF NOT EXISTS ${REMOTE_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"
  echo \"✓ Database ${REMOTE_DB_NAME} ready\"
else
  echo \"ERROR: Database container $DB_CONTAINER not found\" >&2
  exit 2
fi
'"

print ""
print "Step 3: Uploading data file to remote server..."
sshpass -p "$REMOTE_PASS" scp -P $REMOTE_PORT -o StrictHostKeyChecking=no "$EXPORT_FILE" "$REMOTE_USER@$REMOTE_HOST:/tmp/django_data.json"
print "✓ Data file uploaded to /tmp/django_data.json"

print ""
print "════════════════════════════════════════════════════════════════"
print "Migration preparation complete!"
print "════════════════════════════════════════════════════════════════"
print ""
print "MySQL Database Connection Info:"
print "  Host: $DB_CONTAINER (or container IP/localhost if from host)"
print "  Database: $REMOTE_DB_NAME"
print "  User: $REMOTE_DB_USER"
print "  Password: $REMOTE_DB_PASS"
print ""
print "NEXT STEPS (to complete on remote Django app):"
print ""
print "1. Update your Django settings.py DATABASES configuration:"
print ""
print "   DATABASES = {"
print "       'default': {"
print "           'ENGINE': 'django.db.backends.mysql',"
print "           'NAME': '$REMOTE_DB_NAME',"
print "           'USER': '$REMOTE_DB_USER',"
print "           'PASSWORD': '$REMOTE_DB_PASS',"
print "           'HOST': '$DB_CONTAINER',  # or use container IP"
print "           'PORT': '3306',"
print "           'OPTIONS': {"
print "               'charset': 'utf8mb4',"
print "               'init_command': \"SET sql_mode='STRICT_TRANS_TABLES'\","
print "           }"
print "       }"
print "   }"
print ""
print "2. Install mysqlclient in your Django app:"
print "   pip install mysqlclient"
print ""
print "3. Run migrations to create schema:"
print "   python manage.py migrate"
print ""
print "4. Load the data:"
print "   python manage.py loaddata /tmp/django_data.json"
print ""
print "5. Create superuser if needed:"
print "   python manage.py createsuperuser"
print ""
print "════════════════════════════════════════════════════════════════"
