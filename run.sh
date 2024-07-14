#!/bin/bash

# Navigate to the directory containing the docker-compose.yml file
cd /root/olx-bot

# Start the Docker Compose services
docker compose up -d

# Pause the script for 10 minutes
sleep 600

# Stop and remove the Docker Compose services, but keep the volumes
docker-compose down