#!/usr/bin/env bash
set -euo pipefail

# Build Docker image for dadgan.com Django site

IMAGE_NAME="dadgan-django"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

print() { printf "%s\n" "$*"; }

print "Building Docker image: $FULL_IMAGE_NAME"
print "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker build -t "$FULL_IMAGE_NAME" .

if [ $? -eq 0 ]; then
  print "✓ Image built successfully: $FULL_IMAGE_NAME"
  print ""
  print "Image size:"
  docker images "$IMAGE_NAME:$IMAGE_TAG"
  print ""
  print "To save image as tar for upload:"
  print "  docker save $FULL_IMAGE_NAME -o dadgan-django-${IMAGE_TAG}.tar"
  print ""
  print "To deploy using sync_and_deploy.sh:"
  print "  ./sync_and_deploy.sh --load-image ./dadgan-django-${IMAGE_TAG}.tar"
  print ""
  print "Or push to registry and deploy:"
  print "  docker tag $FULL_IMAGE_NAME your-registry/$FULL_IMAGE_NAME"
  print "  docker push your-registry/$FULL_IMAGE_NAME"
  print "  ./sync_and_deploy.sh --image your-registry/$FULL_IMAGE_NAME"
else
  print "✗ Build failed"
  exit 1
fi
