#!/bin/bash

CONTAINER_REGISTRY=$CONTAINER_REGISTRY

# Properly parse IMAGE ID, NAME, and TAG
docker image ls --format "{{.ID}},{{.Repository}},{{.Tag}}" | while IFS=',' read -r IMAGE_ID NAME TAG; do
    echo "Running command for Image ID: $IMAGE_ID, Name: $NAME, Tag: $TAG"

    # Ensure no empty variables (skip untagged images)
    if [[ -n "$NAME" && "$(echo "$NAME" | awk -F'/' '{print $1}')" == "agentflowcr.azurecr.io" && -n "$TAG" ]]; then
        echo "docker push ${NAME}:${TAG}"
        docker push "${NAME}:${TAG}"
    else
        echo "Skipping image $IMAGE_ID due to missing name or tag."
    fi
done

