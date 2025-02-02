#!/bin/bash

DOCKER_REGISTRY=$DOCKER_REGISTRY

# Properly parse IMAGE ID, NAME, and TAG
docker image ls --format "{{.ID}},{{.Repository}},{{.Tag}}" | while IFS=',' read -r IMAGE_ID NAME TAG; do
    # Extract the last segment of the image name (e.g., from db/pgadmin4 to pgadmin4)
    LAST_NAME=$(echo "$NAME" | awk -F'/' '{print $NF}')

    # Default TAG to 'latest' if it's empty
    TAG=${TAG:-latest}

    echo "Running tag command for Image ID: $IMAGE_ID, Name: $LAST_NAME, Tag: $TAG\n"
    
    echo "docker tag $IMAGE_ID ${DOCKER_REGISTRY}/${LAST_NAME}:${TAG}\n"
    # Tag the image with the new name
    docker tag $IMAGE_ID "${DOCKER_REGISTRY}/${LAST_NAME}:${TAG}"

    docker image ls

    # Delete the original image
    # echo "Removing original image with Image ID: $IMAGE_ID"
    # docker rmi --force $IMAGE_ID
    
    docker image ls

done
