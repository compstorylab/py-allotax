#!/bin/bash
# Check for Docker or Podman
if docker info &> /dev/null; then
    CONTAINER_ENGINE="docker"
elif podman info &> /dev/null; then
    CONTAINER_ENGINE="podman"
else
    echo "Error: Neither Docker nor Podman is installed on this system. Please install one of them to continue."
    exit 1
fi
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
nvm use --lts
# Build package
$CONTAINER_ENGINE build --no-cache -t allotax .
$CONTAINER_ENGINE rm allotax
$CONTAINER_ENGINE run --name allotax allotax
$CONTAINER_ENGINE cp allotax:/app/dist ./dist
$CONTAINER_ENGINE stop allotax
