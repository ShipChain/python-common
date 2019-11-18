## Base image with python and entrypoint scripts ##
## ============================================= ##
FROM python:3.6.9-alpine3.10 AS base

LABEL maintainer="Adam Hodges <ahodges@shipchain.io>"

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

# Essential packages for our app environment
RUN apk add --no-cache bash curl binutils linux-headers && \
    curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python && \
    apk del curl

# Install and configure virtualenv
RUN pip install virtualenv==16.3.*
ENV VIRTUAL_ENV=/app/.virtualenv
ENV PATH=$VIRTUAL_ENV/bin:/root/.poetry/bin:$PATH

# Initialize app dir and entrypoint scripts
RUN mkdir /app
WORKDIR /app
ENV XDG_CONFIG_HOME /app/.config
COPY compose/image /
RUN chmod +x /*.sh
ENTRYPOINT ["/entrypoint.sh"]

## Image with system dependencies for building ##
## =========================================== ##
FROM base AS build

# Essential packages for building python packages
RUN apk add --no-cache build-base git libffi-dev openssl-dev su-exec

## Image with additional dependencies for local docker usage ##
## ========================================================= ##
FROM build as local
RUN chmod -R 777 /root/  ## Grant all local users access to poetry

## Image with dev-dependencies ##
## =========================== ##
FROM build AS test

COPY . /app/
RUN \[ -d "$VIRTUAL_ENV" \] || virtualenv "$VIRTUAL_ENV"
RUN . "$VIRTUAL_ENV/bin/activate" && poetry install