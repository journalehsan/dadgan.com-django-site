#!/usr/bin/env bash
set -euo pipefail

# Sync and deploy script for replacing the remote dadgan_app container
# Stops old container, deploys new one on port 4436

REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PORT=22
REMOTE_PASS='Trk@#1403'

CONTAINER_NAME="dadgan_app"
EXTERNAL_PORT=4436
INTERNAL_PORT=80
REMOTE_TMP_DIR="/tmp/deploy_$$"

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }

usage() {
  cat <<EOF
Usage: $0 (--image IMAGE | --load-image PATH) [--container NAME]

Options:
  --image IMAGE        Docker image name (on remote or to pull)
  --load-image PATH    Local image tar to upload and load
  --container NAME     Container name (default: $CONTAINER_NAME)
  --help               Show help

Examples:
  $0 --image dadgan-django:latest
  $0 --load-image ./dadgan-image.tar
EOF
}

IMAGE_TO_PULL=""
LOCAL_IMAGE_TAR=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --image) IMAGE_TO_PULL="$2"; shift 2;;
    --load-image) LOCAL_IMAGE_TAR="$2"; shift 2;;
    --container) CONTAINER_NAME="$2"; shift 2;;
    --help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 2;;
  esac
done

if [ -z "$IMAGE_TO_PULL" ] && [ -z "$LOCAL_IMAGE_TAR" ]; then
  err "Either --image or --load-image is required"
  usage
  exit 2
fi

if ! command -v sshpass >/dev/null 2>&1; then
  err "sshpass is required. Install and re-run."
  exit 1
fi

print "Preparing remote deploy directory: $REMOTE_TMP_DIR"
sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_TMP_DIR"

print "Stopping existing container and creating backup..."
sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
if docker ps -a --format \"{{.Names}}\" | grep -w $CONTAINER_NAME >/dev/null 2>&1; then
  echo \"Stopping container: $CONTAINER_NAME\"
  docker stop $CONTAINER_NAME || true
  echo \"Saving backup to $REMOTE_TMP_DIR/${CONTAINER_NAME}_backup.tar\"
  docker export $CONTAINER_NAME -o $REMOTE_TMP_DIR/${CONTAINER_NAME}_backup.tar || true
  docker commit $CONTAINER_NAME backup_image_${CONTAINER_NAME} || true
  docker save backup_image_${CONTAINER_NAME} -o $REMOTE_TMP_DIR/${CONTAINER_NAME}_backup_image.tar || true
  echo \"Removing old container\"
  docker rm $CONTAINER_NAME || true
else
  echo \"Container $CONTAINER_NAME not found\"
fi
'"

if [ -n "$LOCAL_IMAGE_TAR" ]; then
  if [ ! -f "$LOCAL_IMAGE_TAR" ]; then
    err "Local tar not found: $LOCAL_IMAGE_TAR"
    exit 1
  fi
  print "Uploading image tar to remote..."
  sshpass -p "$REMOTE_PASS" scp -P $REMOTE_PORT -o StrictHostKeyChecking=no "$LOCAL_IMAGE_TAR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_TMP_DIR/"
  BASENAME=$(basename "$LOCAL_IMAGE_TAR")
  print "Loading image on remote..."
  sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "docker load -i $REMOTE_TMP_DIR/$BASENAME"
else
  RUN_IMAGE="$IMAGE_TO_PULL"
fi

if [ -z "${RUN_IMAGE:-}" ]; then
  RUN_IMAGE="$IMAGE_TO_PULL"
fi

print "Running new container: $RUN_IMAGE as $CONTAINER_NAME"
sshpass -p "$REMOTE_PASS" ssh -p $REMOTE_PORT -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" bash -c "'
set -e
docker run -d \
  --name $CONTAINER_NAME \
  -p ${EXTERNAL_PORT}:${INTERNAL_PORT} \
  --restart unless-stopped \
  --network docker-mariadb-phpmyadmin_default \
  -e DB_ENGINE=mysql \
  -e DB_NAME=dadgan_django \
  -e DB_USER=root \
  -e DB_PASSWORD=my-secret-pw \
  -e DB_HOST=docker-mariadb-phpmyadmin-mariadb-1 \
  -e DB_PORT=3306 \
  -e DJANGO_SECRET_KEY=prod-secret-$(date +%s) \
  -e DJANGO_DEBUG=False \
  -e DJANGO_ALLOWED_HOSTS=dadgan.com,www.dadgan.com,localhost \
  $RUN_IMAGE
'"

print ""
print "✓ Container deployed successfully!"
print ""
print "Next steps:"
print "1. Run migrations: docker exec $CONTAINER_NAME python manage.py migrate"
print "2. Load data: docker exec $CONTAINER_NAME python manage.py loaddata /tmp/django_data.json"
print "   (copy file first: docker cp /tmp/django_data.json $CONTAINER_NAME:/tmp/)"
print "3. Create superuser: docker exec -it $CONTAINER_NAME python manage.py createsuperuser"
print "4. Test: curl http://localhost:$EXTERNAL_PORT or https://dadgan.com"
print ""
print "Backups at: $REMOTE_TMP_DIR on remote"
