#!/bin/bash

# Simple deployment script for HVAC CRM/ERP application
# This script sets up the application to run with Nginx on a server

# Exit on error
set -e

# Configuration
APP_NAME="hvac-crm-erp"
DOMAIN="savelal.example.com"  # Replace with your actual domain
APP_PORT=8501

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  HVAC CRM/ERP Simple Deployment Script  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install pip3 first.${NC}"
    exit 1
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Nginx is not installed. Installing Nginx...${NC}"
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Create a Python virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

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

# Configure Nginx
echo -e "${YELLOW}Configuring Nginx...${NC}"
sudo cp nginx_simple.conf /etc/nginx/sites-available/${DOMAIN}.conf
sudo sed -i "s/savelal.example.com/${DOMAIN}/g" /etc/nginx/sites-available/${DOMAIN}.conf
sudo ln -sf /etc/nginx/sites-available/${DOMAIN}.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Create a systemd service file
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > ${APP_NAME}.service << EOF
[Unit]
Description=HVAC CRM/ERP Streamlit Application
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/streamlit run $(pwd)/app.py --server.port=${APP_PORT} --server.address=0.0.0.0
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=${APP_NAME}
Environment="PATH=$(pwd)/venv/bin:$PATH"
Environment="PYTHONPATH=$(pwd)"

[Install]
WantedBy=multi-user.target
EOF

sudo mv ${APP_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}
sudo systemctl start ${APP_NAME}

# Check if service is running
if systemctl is-active --quiet ${APP_NAME}; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}The application is now running at http://${DOMAIN}${NC}"
else
    echo -e "${RED}Deployment failed. Please check the logs with 'journalctl -u ${APP_NAME}'.${NC}"
    exit 1
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment Complete                   ${NC}"
echo -e "${GREEN}=========================================${NC}"
