#!/bin/bash

# Docker deployment script for HVAC CRM/ERP application
# This script builds and runs the application using Docker

# Exit on error
set -e

# Configuration
APP_NAME="hvac-crm-erp"
PORT=${PORT:-8501}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  HVAC CRM/ERP Docker Deployment Script  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please update the .env file with your actual configuration values.${NC}"
    else
        echo -e "${RED}.env.example file not found. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Build and run the Docker container
echo -e "${YELLOW}Building and running Docker container...${NC}"
docker build -t ${APP_NAME} .
docker run -d --name ${APP_NAME} -p ${PORT}:8501 -e PORT=${PORT} --restart always ${APP_NAME}

# Check if container is running
if docker ps | grep -q ${APP_NAME}; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}The application is now running at http://localhost:${PORT}${NC}"
else
    echo -e "${RED}Deployment failed. Please check the logs with 'docker logs ${APP_NAME}'.${NC}"
    exit 1
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment Complete                   ${NC}"
echo -e "${GREEN}=========================================${NC}"
