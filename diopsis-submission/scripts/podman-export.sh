#!/usr/bin/env sh
# set -Euo pipefail

IMAGE_NAME="podman-diopsis_class_alg"
echo "exporting $IMAGE_NAME"
podman build -t "$IMAGE_NAME" .
podman save "$IMAGE_NAME" | gzip > "$IMAGE_NAME".tar.gz
