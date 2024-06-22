# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 docker.io/library/python:3.9

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

RUN groupadd -r user && useradd -m --no-log-init -r -g user user

RUN mkdir -p /opt/app /input /output \
    && chown user:user /opt/app /input /output

USER user
WORKDIR /opt/app

ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user:user requirements.txt /opt/app/
COPY --chown=user:user name_to_ancestors_with_levels.csv /opt/app/
COPY --chown=user:user model.pth /opt/app/
RUN python -m pip install \
    --user \
    --no-cache-dir \
    --no-color \
    --requirement /opt/app/requirements.txt

# Copy the source code into the container.
COPY --chown=user:user . /opt/app/

ENTRYPOINT [ "python", "main.py", "/input", "/output/predictions.csv" ]
