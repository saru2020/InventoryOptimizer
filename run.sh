#!/bin/bash

# Name of your Docker image
DOCKER_IMAGE=inventory_optimizer
# Name of your Docker container
DOCKER_CONTAINER_NAME=inventory_optimizer

# Set the name of your Docker image
DOCKER_IMAGE_NAME="$DOCKER_IMAGE"

# Remove the existing container if it exists
# docker rm -f $DOCKER_CONTAINER

# docker rm -f $DOCKER_IMAGE_NAME 2>/dev/null || true

# Stop and forcefully remove existing Docker container if it exists
docker rm -f $DOCKER_CONTAINER_NAME 2>/dev/null || true

docker build -t $DOCKER_IMAGE_NAME .

# Run Docker container
docker run -v $(pwd)/data:/data --name $DOCKER_CONTAINER_NAME $DOCKER_IMAGE_NAME #--mount type=bind,source=`pwd`,target=/usr/src/app
