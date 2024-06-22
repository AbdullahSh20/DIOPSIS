#!/usr/bin/env bash

IMAGE_NAME="diopsis_class_alg"
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"


echo "exporting $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

VOLUME_SUFFIX=$(dd if=/dev/urandom bs=32 count=1 | md5sum | cut --delimiter=' ' --fields=1)
# Maximum is currently 30g, configurable in your algorithm image settings on grand challenge
MEM_LIMIT="4g"

docker volume create $IMAGE_NAME-output-$VOLUME_SUFFIX

# Do not change any of the parameters to docker run, these are fixed
docker run --rm \
        --memory="${MEM_LIMIT}" \
        --memory-swap="${MEM_LIMIT}" \
        --network="none" \
        --cap-drop="ALL" \
        --security-opt="no-new-privileges" \
        --shm-size="128m" \
        --pids-limit="256" \
        -v $SCRIPTPATH/../example/input:/input/:z \
        -v $IMAGE_NAME-output-$VOLUME_SUFFIX:/output/ \
        $IMAGE_NAME

docker run --rm \
        -v $IMAGE_NAME-output-$VOLUME_SUFFIX:/output/ \
        python:3.10-slim cat /output/predictions.csv

docker run --rm \
        -v $IMAGE_NAME-output-$VOLUME_SUFFIX:/output/ \
        -v $SCRIPTPATH/../example/input:/input:z \
        -v $SCRIPTPATH/../example/expected:/expected:z \
        python:3.10-slim python -c "import csv, sys; f1 = list(csv.reader(open('/output/predictions.csv'))); f2 = list(csv.reader(open('/expected/expected_predictions.csv'))); sys.exit(f1 != f2);"

if [ $? -eq 0 ]; then
    echo "Tests successfully passed..."
else
    echo "Expected output was not found..."
fi

docker volume rm $IMAGE_NAME-output-$VOLUME_SUFFIX
