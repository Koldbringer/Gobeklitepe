#!/bin/bash

# Exit on error
set -e

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p assets
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Print success message
echo "Build completed successfully!"
