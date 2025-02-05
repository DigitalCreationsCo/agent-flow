# Install containerapp extension
az extension add --name containerapp

# Create environment
az containerapp env create \
  --name my-environment \
  --resource-group agentflow \
  --location eastus

# Deploy using Docker Compose file
az containerapp up \
  --name agentflow \
  --resource-group agentflow \
#   --environment my-environment \
  --compose-file ../../deploy/docker-compose.azure.yml
