#!/usr/bin/env bash
set -Euo pipefail
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
DIND_IMAGE=docker:24.0.9-dind
DIND_CONTAINER_NAME=dind

function onexit {
    docker stop $DIND_CONTAINER_NAME 2>&1 > /dev/null
    docker rm $DIND_CONTAINER_NAME 2>&1 > /dev/null
}

trap "onexit" EXIT

onexit 2>&1 > /dev/null

docker run -v $SCRIPTPATH/..:/app:z --workdir=/app --privileged -d --name $DIND_CONTAINER_NAME $DIND_IMAGE

docker exec -ti $DIND_CONTAINER_NAME "${@:-sh}"
