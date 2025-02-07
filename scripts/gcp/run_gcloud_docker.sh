# Build the image
docker build -f scripts/gcp/gcp.Dockerfile -t gcloud-cli-docker . || { echo "Docker build failed"; exit 1; }

docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /Users/bryantmejia/.docker:/root/.docker \
  -v $(pwd):/workspace \
  -w /workspace \
  gcloud-cli-docker