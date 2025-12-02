#!/usr/bin/env bash
set -euo pipefail

# Build Docker image on remote server (workaround for local network issues)

REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PORT=22
REMOTE_PASS='Trk@#1403'
REMOTE_BUILD_DIR="/tmp/dadgan-build"
IMAGE_NAME="dadgan-django:latest"

print() { printf "%s\n" "$*"; }

print "Step 1: Creating remote build directory..."
sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
  "rm -rf $REMOTE_BUILD_DIR && mkdir -p $REMOTE_BUILD_DIR"

print "Step 2: Uploading project files..."
rsync -avz --progress \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.sqlite3' \
  --exclude='tmp_sql_migrate' \
  --exclude='laravel_backup' \
  --exclude='*.tar' \
  -e "sshpass -p '$REMOTE_PASS' ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no" \
  ./ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_BUILD_DIR/"

print "Step 3: Building Docker image on remote server..."
sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
cd $REMOTE_BUILD_DIR
echo \"Building image: $IMAGE_NAME\"
docker build -t $IMAGE_NAME .
echo \"Build complete!\"
docker images | grep dadgan-django
'"

print ""
print "✓ Docker image built successfully on remote server!"
print ""
print "Next step: Deploy the container"
print "  Run: ./sync_and_deploy.sh --image $IMAGE_NAME"
print ""
print "Or deploy manually:"
print "  sshpass -p '$REMOTE_PASS' ssh $REMOTE_USER@$REMOTE_HOST"
print "  (then see DEPLOYMENT_GUIDE.md Step 3)"
