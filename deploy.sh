#!/usr/bin/env bash
set -euo pipefail

# Complete deployment wrapper for dadgan.com Django site
# Runs all steps: export data, build image, deploy container, run migrations

REMOTE_USER="rocky"
REMOTE_HOST="37.32.13.22"
REMOTE_PASS='Trk@#1403'

print() { printf "%s\n" "$*"; }
err() { printf "ERROR: %s\n" "$*" >&2; }
success() { printf "✓ %s\n" "$*"; }

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Complete deployment pipeline for dadgan.com Django site.

Options:
  --skip-export       Skip data export (use if data hasn't changed)
  --skip-build        Skip Docker image build (use existing image)
  --skip-migration    Skip running database migrations
  --help              Show this help

This script will:
1. Export local SQLite data to JSON
2. Upload data to remote server
3. Build Docker image on remote server
4. Stop old container and deploy new one
5. Run database migrations
6. Verify deployment

EOF
}

SKIP_EXPORT=false
SKIP_BUILD=false
SKIP_MIGRATION=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-export) SKIP_EXPORT=true; shift;;
    --skip-build) SKIP_BUILD=true; shift;;
    --skip-migration) SKIP_MIGRATION=true; shift;;
    --help) usage; exit 0;;
    *) err "Unknown option: $1"; usage; exit 2;;
  esac
done

print "════════════════════════════════════════════════════════════════"
print "  dadgan.com Complete Deployment Pipeline"
print "════════════════════════════════════════════════════════════════"
print ""

# Step 1: Export data (optional)
if [ "$SKIP_EXPORT" = false ]; then
  print "[1/5] Exporting local Django data..."
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  fi
  
  mkdir -p ./data_export
  
  if python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions \
    > ./data_export/django_data.json; then
    success "Data exported to ./data_export/django_data.json"
    ls -lh ./data_export/django_data.json
    
    # Upload to remote
    print "  Uploading data to remote server..."
    sshpass -p "$REMOTE_PASS" scp -P 22 -o StrictHostKeyChecking=no \
      ./data_export/django_data.json "$REMOTE_USER@$REMOTE_HOST:/tmp/" 2>&1 | grep -v "WARNING" || true
    success "Data uploaded to /tmp/django_data.json"
  else
    err "Data export failed"
    exit 1
  fi
else
  print "[1/5] Skipping data export (--skip-export)"
fi

print ""

# Step 2: Build Docker image
if [ "$SKIP_BUILD" = false ]; then
  print "[2/5] Building Docker image on remote server..."
  
  if bash ./build_remote.sh 2>&1 | grep -E "(Uploading|Building|Build complete|✓)" | grep -v "WARNING"; then
    success "Docker image built successfully"
  else
    err "Docker build failed"
    exit 1
  fi
else
  print "[2/5] Skipping Docker build (--skip-build)"
fi

print ""

# Step 3: Deploy container
print "[3/5] Deploying new container..."

if bash ./sync_and_deploy.sh --image dadgan-django:latest 2>&1 | grep -E "(Stopping|Running|deployed)" | grep -v "WARNING"; then
  success "Container deployed"
else
  err "Deployment failed"
  exit 1
fi

print ""

# Step 4: Run migrations
if [ "$SKIP_MIGRATION" = false ]; then
  print "[4/5] Running database migrations..."
  
  sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
    "docker exec dadgan_app python manage.py migrate" 2>&1 | grep -v "WARNING" | tail -5
  
  success "Migrations applied"
else
  print "[4/5] Skipping migrations (--skip-migration)"
fi

print ""

# Step 5: Verify deployment
print "[5/5] Verifying deployment..."

# Check container status
CONTAINER_STATUS=$(sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
  "docker ps --filter name=dadgan_app --format '{{.Status}}'" 2>&1 | grep -v "WARNING")

if echo "$CONTAINER_STATUS" | grep -q "Up"; then
  success "Container is running: $CONTAINER_STATUS"
else
  err "Container is not running!"
  exit 1
fi

# Test HTTP response
HTTP_CODE=$(sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
  "curl -s -o /dev/null -w '%{http_code}' http://localhost:4436/" 2>&1 | grep -v "WARNING")

if [ "$HTTP_CODE" = "200" ]; then
  success "HTTP response: $HTTP_CODE OK"
else
  err "HTTP response: $HTTP_CODE (expected 200)"
  exit 1
fi

# Test static files
STATIC_CODE=$(sshpass -p "$REMOTE_PASS" ssh -p 22 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" \
  "curl -s -o /dev/null -w '%{http_code}' http://localhost:4436/static/images/favicon.svg" 2>&1 | grep -v "WARNING")

if [ "$STATIC_CODE" = "200" ]; then
  success "Static files: $STATIC_CODE OK"
else
  err "Static files: $STATIC_CODE (expected 200)"
fi

print ""
print "════════════════════════════════════════════════════════════════"
print "  🎉 Deployment Complete!"
print "════════════════════════════════════════════════════════════════"
print ""
print "Site URL: https://dadgan.com"
print "Port: 4436"
print "Container: dadgan_app"
print ""
print "Useful commands:"
print "  View logs:    sshpass -p '$REMOTE_PASS' ssh $REMOTE_USER@$REMOTE_HOST 'docker logs dadgan_app -f'"
print "  Restart:      sshpass -p '$REMOTE_PASS' ssh $REMOTE_USER@$REMOTE_HOST 'docker restart dadgan_app'"
print "  Shell:        sshpass -p '$REMOTE_PASS' ssh $REMOTE_USER@$REMOTE_HOST 'docker exec -it dadgan_app /bin/bash'"
print ""
