# HVAC CRM/ERP System Deployment Guide

This guide provides instructions for deploying the HVAC CRM/ERP system with Nginx.

## Deployment Options

There are two main deployment options:

1. **Docker Deployment**: Using Docker and Docker Compose (recommended for production)
2. **Direct Server Deployment**: Running directly on the server with Nginx

## Prerequisites

- A server with Ubuntu/Debian or similar Linux distribution
- Domain name pointing to your server (e.g., savelal.example.com)
- For Docker deployment: Docker and Docker Compose installed
- For direct deployment: Python 3.9+ installed

## Option 1: Docker Deployment

### 1. Clone the repository

```bash
git clone <repository-url>
cd hvac-crm-erp
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env file with your actual configuration
nano .env
```

### 3. Update domain name

Edit `nginx/savelal.conf` and replace `savelal.example.com` with your actual domain.

### 4. Run the deployment script

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Create necessary directories
- Generate self-signed SSL certificates (replace with real ones for production)
- Build and start Docker containers
- Configure Nginx as a reverse proxy

### 5. Access the application

The application will be available at:
- https://your-domain.com (production)
- http://localhost:8501 (local development)

## Option 2: Direct Server Deployment

### 1. Clone the repository

```bash
git clone <repository-url>
cd hvac-crm-erp
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env file with your actual configuration
nano .env
```

### 3. Update domain name

Edit `nginx_simple.conf` and replace `savelal.example.com` with your actual domain.

### 4. Run the simple deployment script

```bash
chmod +x deploy_simple.sh
./deploy_simple.sh
```

This script will:
- Create a Python virtual environment
- Install dependencies
- Configure Nginx as a reverse proxy
- Create and start a systemd service

### 5. Access the application

The application will be available at http://your-domain.com

## Troubleshooting

### Nginx 404 Not Found Error

If you encounter a 404 Not Found error with Nginx:

1. Check Nginx configuration:
   ```bash
   sudo nginx -t
   ```

2. Check Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Verify the application is running:
   ```bash
   # For Docker deployment
   docker-compose ps
   
   # For direct deployment
   systemctl status hvac-crm-erp
   ```

4. Check if the application port is accessible:
   ```bash
   curl http://localhost:8501
   ```

### SSL Certificate Issues

If you encounter SSL certificate issues:

1. For production, replace the self-signed certificates with real ones:
   ```bash
   # Using Let's Encrypt
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. Update the Nginx configuration to use the new certificates.

## Maintenance

### Updating the Application

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Restart the application:
   ```bash
   # For Docker deployment
   docker-compose restart
   
   # For direct deployment
   sudo systemctl restart hvac-crm-erp
   ```

### Backing Up Data

1. Back up the database:
   ```bash
   # For PostgreSQL
   pg_dump -U username -d database_name > backup.sql
   ```

2. Back up environment variables:
   ```bash
   cp .env .env.backup
   ```

## Security Considerations

1. Always use HTTPS in production
2. Use strong passwords for database and services
3. Keep the server and dependencies updated
4. Implement proper authentication and authorization
5. Regularly back up your data
