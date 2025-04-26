#!/bin/bash

# HVAC CRM/ERP Deployment Script
# This script automates the deployment process for the HVAC CRM/ERP application

# Exit on error
set -e

# Configuration
APP_NAME="hvac-crm-erp"
DOMAIN="hvac-crm.example.com"  # Replace with your actual domain

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  HVAC CRM/ERP Deployment Script        ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Check if SSL certificates exist
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo -e "${YELLOW}SSL certificates not found. Creating self-signed certificates for development.${NC}"
    echo -e "${YELLOW}For production, replace these with real certificates from a certificate authority.${NC}"
    
    # Generate self-signed SSL certificates for development
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/CN=${DOMAIN}/O=HVAC CRM/C=PL"
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

# Build and start the containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose build
docker-compose up -d

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}The application is now running at https://${DOMAIN}${NC}"
    echo -e "${GREEN}For local development, access the application at http://localhost:8501${NC}"
else
    echo -e "${RED}Deployment failed. Please check the logs with 'docker-compose logs'.${NC}"
    exit 1
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment Complete                   ${NC}"
echo -e "${GREEN}=========================================${NC}"
