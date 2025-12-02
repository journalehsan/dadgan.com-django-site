#!/usr/bin/env bash
set -euo pipefail

# Migrate local Django sqlite3 database to a remote MySQL (MariaDB) running inside Docker on a remote host.
#
# Usage:
#   ./migrate_sqlite_to_mysql.sh            # uses defaults at top of file
#   ./migrate_sqlite_to_mysql.sh --dbfile path/to/db.sqlite3 --remote-db new_db_name
#
# NOTE: This script tries to convert common SQLite schema constructs to MySQL-compatible SQL,
# but complex schemas or custom SQL may require manual adjustments. Review the generated SQL
# at the temporary path printed by the script before importing.

### Configurable variables (edit as needed) ###
SQLITE_DB="./db.sqlite3"
TMP_DIR="./tmp_sql_migrate"

# Remote server access
REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PORT=22
REMOTE_PASS='Trk@#1403'

# Remote MySQL (mariadb) container name and credentials
DB_CONTAINER="docker-mariadb-phpmyadmin-mariadb-1"
REMOTE_DB_NAME="c1dadgan"
REMOTE_DB_USER="root"
REMOTE_DB_PASS="my-secret-pw"

### End config ###

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }

usage() {
  cat <<EOF
Usage: $0 [--dbfile PATH] [--remote-db NAME]

Options:
  --dbfile PATH     Path to sqlite3 db file (default: $SQLITE_DB)
  --remote-db NAME  Remote MySQL database name (default: $REMOTE_DB_NAME)
  --help            Show this help

The script will:
  - create a sqlite .dump
  - run basic transforms to make it MySQL-compatible
  - upload to remote and import into the configured MariaDB Docker container

Review the converted SQL in the temporary directory before import.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dbfile) SQLITE_DB="$2"; shift 2;;
    --remote-db) REMOTE_DB_NAME="$2"; shift 2;;
    --help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 2;;
  esac
done

if [ ! -f "$SQLITE_DB" ]; then
  err "Sqlite DB not found at: $SQLITE_DB"
  exit 1
fi

mkdir -p "$TMP_DIR"
OUT_DUMP="$TMP_DIR/dump.sqlite.sql"
OUT_MYSQL="$TMP_DIR/dump_mysql.sql"

print "Creating sqlite dump..."
if ! command -v sqlite3 >/dev/null 2>&1; then
  err "sqlite3 is required but not installed."
  exit 1
fi

sqlite3 "$SQLITE_DB" ".dump" > "$OUT_DUMP"
print "Sqlite dump created: $OUT_DUMP"

print "Converting sqlite dump to MySQL-friendly SQL (best-effort)..."
# Strategy: Remove all CREATE TABLE statements and constraints.
# Let Django recreate the schema with `python manage.py migrate`,
# then we'll just import the INSERT statements (data only).
cp "$OUT_DUMP" "$OUT_MYSQL"

# Remove sqlite pragmas and transaction statements
sed -i -E "/^PRAGMA/d; /^BEGIN TRANSACTION/d; /^COMMIT/d; /^sqlite_sequence/d" "$OUT_MYSQL"

# Remove all CREATE TABLE, CREATE INDEX, and CREATE UNIQUE INDEX statements
sed -i -E "/^CREATE TABLE/d; /^CREATE INDEX/d; /^CREATE UNIQUE INDEX/d" "$OUT_MYSQL"

# Remove DEFERRABLE clauses (if any remain in comments or other places)
sed -i -E "s/ DEFERRABLE INITIALLY DEFERRED//gI" "$OUT_MYSQL"

# Keep only INSERT statements - remove empty lines
sed -i "/^$/d" "$OUT_MYSQL"

print "Data-only SQL created (INSERT statements only)."
print "IMPORTANT: You must run 'python manage.py migrate' on the remote Django app"
print "           to create the schema BEFORE importing this data."

print "Converted SQL written to: $OUT_MYSQL"
print "NOTE: This script creates a data-only SQL file (INSERT statements)."
print "      The Django schema will be created by running migrations on the remote server."
print ""
print "Uploading SQL to remote server ($REMOTE_USER@$REMOTE_HOST)..."

if ! command -v sshpass >/dev/null 2>&1; then
  err "sshpass is required for non-interactive remote operations. Install it and re-run."
  exit 1
fi

# Copy converted SQL to remote /tmp
sshpass -p "$REMOTE_PASS" scp -P $REMOTE_PORT -o StrictHostKeyChecking=no "$OUT_MYSQL" "$REMOTE_USER@$REMOTE_HOST:/tmp/dump_mysql.sql"

print "Creating remote DB and importing data..."
print "Note: The remote Django app must have already run 'python manage.py migrate'"
print "      to create the database schema before data import."

sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
if docker inspect $DB_CONTAINER >/dev/null 2>&1; then
  echo \"Creating database ${REMOTE_DB_NAME} if not exists\"
  docker exec $DB_CONTAINER mariadb -u${REMOTE_DB_USER} -p${REMOTE_DB_PASS} -e \"CREATE DATABASE IF NOT EXISTS ${REMOTE_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"
  echo \"Database created/verified.\"
  echo \"\"
  echo \"MANUAL STEP REQUIRED:\"
  echo \"  1. Configure your Django app to use this MySQL database\"
  echo \"  2. Run: python manage.py migrate --database=default\"
  echo \"  3. Then import data: docker exec -i $DB_CONTAINER mariadb -u${REMOTE_DB_USER} -p${REMOTE_DB_PASS} ${REMOTE_DB_NAME} < /tmp/dump_mysql.sql\"
  echo \"\"
  echo \"Data SQL file is at: /tmp/dump_mysql.sql on remote server\"
else
  echo \"Database container $DB_CONTAINER not found on remote host\" >&2
  exit 2
fi
'"

print ""
print "Database ${REMOTE_DB_NAME} created on remote server."
print "Data file uploaded to: /tmp/dump_mysql.sql (on remote)"
print ""
print "NEXT STEPS:"
print "1. Update Django settings.py DATABASES config to use MySQL:"
print "   'ENGINE': 'django.db.backends.mysql',"
print "   'NAME': '${REMOTE_DB_NAME}',"
print "   'USER': '${REMOTE_DB_USER}',"
print "   'PASSWORD': '${REMOTE_DB_PASS}',"
print "   'HOST': 'docker-mariadb-phpmyadmin-mariadb-1'  # or container IP"
print ""
print "2. Run Django migrations to create schema:"
print "   python manage.py migrate"
print ""
print "3. Import data from remote file:"
print "   ssh $REMOTE_USER@$REMOTE_HOST"
print "   docker exec -i $DB_CONTAINER mariadb -u${REMOTE_DB_USER} -p${REMOTE_DB_PASS} ${REMOTE_DB_NAME} < /tmp/dump_mysql.sql"

print "Done."
