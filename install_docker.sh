#!/bin/bash

# Update the package index
echo "Updating package index..."
sudo apt-get update

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker’s official GPG key
echo "Adding Docker GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker's stable repository
echo "Adding Docker repository..."
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update the package index again
echo "Updating package index again..."
sudo apt-get update

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker-ce

# Enable and start Docker service
echo "Starting and enabling Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
echo "Installing Docker Compose..."
DOCKER_COMPOSE_VERSION="1.29.2"  # Change to the latest version if needed
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
echo "Verifying Docker installation..."
sudo docker --version
echo "Verifying Docker Compose installation..."
docker-compose --version

echo "Docker and Docker Compose have been installed successfully!"
