# Build the image
docker build -f scripts/azure/az.Dockerfile -t azure-docker-cli . || { echo "Docker build failed"; exit 1; }

docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /Users/bryantmejia/.docker:/root/.docker \
  -v $HOME/.azure:/root/.azure \
  -v $(pwd):/workspace \
  -w /workspace \
  azure-docker-cli