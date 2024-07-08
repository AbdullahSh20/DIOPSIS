# Arise Challenge Detection Algorithm Template

## Description

This repository contains a template for creating and submitting the detection algorithm to the Arise Challenge.

The included scripts will build a docker image and bundle it into a compressed file, which can then be uploaded via the challenge platform user interface.

## Prerequisites

You will need to install [docker](https://www.docker.com/products/docker-desktop). It is available for all major operating systems.

## Usage

Add you algorithm's implementation in `main.py`. When you are ready to submit your algorithm, it can be exported with one of the methods listed below.

Your algorithm implementation starts in the `predict` function, before `results = [...` (See [here](main.py#L19)). 

## Algorithm Output Format

The following code snippet illustrates the required output format for the algorithm you are implementing. Each prediction for an image (the algorithm only processes one image at a time) should follow this structure:
```py
{
    "annotations": [
        {
            "labels": [
                {
                    "probability": 1.0,
                    "name": "Object",
                    "color": "#e1e7d9ff",
                }
            ],
            "shape": {
                "x": 2203,
                "y": 1592,
                "width": 405,
                "height": 769,
                "type": "RECTANGLE",
            },
        }
    ]
}
```

If multiple objects are detected in one image, each object should be included as a separate entry in the "annotations" list.

### Adding additional files
**NOTE**: Adding files to the container needs to happen in (potentially) two places: the Dockerfile has a line which should copy everything into the container from the current directory: `COPY --chown=user:user . /opt/app/`, the `.` means everything in this directory, but first docker checks what files is it allowed to look for in the  `.dockerignore` file. Opening up `.dockerignore`, you may notice that our current setup disregards everything with the star symbol `*`, and newline by newline enables just a few files with the `!` mark.

> **EXAMPLE**: you want to add the weights which are named `weights.pkl`, you need to allow it in `.dockerignore`: `! weights.pkl` 


## Testing

The folder `./example/input` contains an example input image. The expected prediction for this image can be found in `./example/output/expected_predictions.csv`.
To test if your algorithm produces what you expect, change the values in `./example/output/expected_predictions.csv` to your expected outputs, then run:
```sh
./scripts/docker-test.sh
```

On success, you should see the text `Tests successfully passed...`.

## Exporting on Windows / Mac

From this directory launch a terminal / command prompt / powershell, then:
```cmd
docker run -v .:/app --workdir=/app --privileged --name dind docker:24.0.9-dind
```

Go to Docker Desktop and in the containers there should be `dind`, and on the three dots, it should appear `Open in terminal` then run `./scripts/docker-export.sh`.

This will create diopsis_class_alg.tar.gz which can be uploaded via the challenge platform.

## Exporting on Linux

We provide various ways to export your algorithm:
- `./scripts/docker-export.sh` (you will need to have a Docker version 24 or lower, check with `docker -v`)
- `./scripts/podman-export.sh` (need podman installed `sudo apt install podman`)
- `./scripts/docker24-shell.sh` (when your docker version is higher than 24)
    - to work with this, after you run it you get a shell, and inside the shell run `./scripts/docker-export.sh`
