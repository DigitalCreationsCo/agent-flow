#!/bin/bash

# Ensure the DOCKER_REGISTRY environment variable is set
export DOCKER_REGISTRY="agentflowcr.azurecr.io"
export DOCKER_CLIENT_TIMEOUT=10000
export COMPOSE_HTTP_TIMEOUT=10000

# Navigate to the deploy directory
cd "../../deploy" || { echo "Deploy directory not found"; exit 1; }

# Pull images with Docker Compose
docker compose pull || { echo "Docker Compose build failed"; exit 1; }

# Navigate to the scripts directory
cd "../scripts/azure" || { echo "Scripts directory not found"; exit 1; }

# Run the tagging script
if [[ -f ./tag_all_images.sh ]]; then
  /bin/bash ./tag_all_images.sh
  if [[ $? -ne 0 ]]; then
    echo "Tagging script failed"
    exit 1
  fi
else
  echo "Tagging script not found"
  exit 1
fi

# Run the pushing script
if [[ -f ./push_all_images.sh ]]; then
  /bin/bash ./push_all_images.sh
  if [[ $? -ne 0 ]]; then
    echo "Pushing script failed"
    exit 1
  fi
else
  echo "Pushing script not found"
  exit 1
fi

# Go back to the deploy directory for Azure-specific Compose
cd "../../deploy" || { echo "Deploy directory not found"; exit 1; }

# Use the Azure-specific Docker Compose file
docker compose --file "docker-compose.azure.yml" up
