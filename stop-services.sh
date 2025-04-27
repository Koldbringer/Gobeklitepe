#!/bin/bash

# Stop all services using Docker Compose
docker-compose -f docker-compose-full.yml down

echo "All services have been stopped."
