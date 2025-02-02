# Build the image
docker build -f az.Dockerfile -t azure-docker-cli . || { echo "Docker build failed"; exit 1; }

# Run the container with Docker socket mounted
docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /Users/bryantmejia/.docker:/root/.docker \
  -v $HOME/.azure:/root/.azure \
  azure-docker-cli

# If you need to mount your current directory as well, add:
# docker run -it \
#   -v /var/run/docker.sock:/var/run/docker.sock \
#   -v $HOME/.azure:/root/.azure \
#   -v $(pwd):/workspace \
#   -w /workspace \
#   azure-docker-cli