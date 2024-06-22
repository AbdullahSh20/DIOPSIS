#!/usr/bin/env sh
# set -Euo pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

version=$(docker version --format '{{.Server.Version}}' | cut -d '.'  -f 1)
if [ "24" -lt "$version" ]; then 
    echo "Versions of docker higher than 24 are not supported, see README for alternative solutions.";
    echo " Exiting...";
    exit 1
fi

IMAGE_NAME="diopsis_class_alg"
echo "exporting $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .
docker save "$IMAGE_NAME" | gzip -c > "$IMAGE_NAME".tar.gz