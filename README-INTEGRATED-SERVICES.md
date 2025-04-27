# HVAC CRM/ERP Integrated Services

This document provides information on how to use the integrated services in the HVAC CRM/ERP system.

## Overview

The HVAC CRM/ERP system now includes the following integrated services:

1. **n8n** - Workflow automation platform
2. **Mastra AI** - AI agent framework
3. **Maxun** - Web data extraction tool
4. **MinIO** - Object storage for documents and files
5. **PostgreSQL** - Database for all services
6. **Redis** - Caching and message broker

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Git installed
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Koldbringer/Gobeklitepe.git
   cd Gobeklitepe
   ```

2. Copy the environment template and update it with your settings:
   ```bash
   cp .env.template .env
   # Edit .env with your preferred text editor
   ```

3. Start all services:
   - On Linux/Mac:
     ```bash
     chmod +x start-services.sh
     ./start-services.sh
     ```
   - On Windows:
     ```bash
     start-services.bat
     ```

4. Wait for all services to start (this may take a few minutes on first run)

5. Access the services:
   - HVAC CRM/ERP: http://localhost:8501
   - n8n Workflow Automation: http://localhost:5678
   - Mastra AI Agent Framework: http://localhost:3000
   - Maxun Web Data Extraction (Frontend): http://localhost:5173
   - Maxun Web Data Extraction (Backend): http://localhost:8080
   - MinIO Object Storage: http://localhost:9001

### Stopping Services

To stop all services:
- On Linux/Mac:
  ```bash
  chmod +x stop-services.sh
  ./stop-services.sh
  ```
- On Windows:
  ```bash
  stop-services.bat
  ```

## Using the Integrated Services

### n8n Workflow Automation

n8n is a powerful workflow automation tool that can be used to automate various tasks in the HVAC CRM/ERP system.

#### Example Use Cases:
- Automatically create service orders based on sensor data
- Send notifications when inventory levels are low
- Generate reports and send them via email
- Integrate with external APIs and services

#### Getting Started:
1. Access n8n at http://localhost:5678
2. Create a new workflow
3. Use the HTTP node to connect to the HVAC CRM/ERP API
4. Set up triggers and actions based on your requirements

### Mastra AI Agent Framework

Mastra AI is an agent framework that can be used to create AI-powered assistants for the HVAC CRM/ERP system.

#### Example Use Cases:
- Create a customer service chatbot
- Develop an AI assistant for technicians
- Build an AI-powered recommendation system for parts and services
- Automate document analysis and data extraction

#### Getting Started:
1. Access Mastra AI at http://localhost:3000
2. Create a new agent
3. Configure the agent with the required skills and knowledge
4. Deploy the agent to the HVAC CRM/ERP system

### Maxun Web Data Extraction

Maxun is a web data extraction tool that can be used to gather data from various sources for the HVAC CRM/ERP system.

#### Example Use Cases:
- Extract product information from manufacturer websites
- Gather pricing data from competitors
- Collect weather data for predictive maintenance
- Extract information from PDF documents and forms

#### Getting Started:
1. Access Maxun Frontend at http://localhost:5173
2. Create a new extraction project
3. Configure the extraction rules
4. Run the extraction and view the results
5. Use the Maxun API at http://localhost:8080 to integrate with other services

### MinIO Object Storage

MinIO is an object storage system used to store documents, images, and other files in the HVAC CRM/ERP system.

#### Example Use Cases:
- Store customer documents and contracts
- Save equipment manuals and documentation
- Archive service reports and photos
- Store backup files and exports

#### Getting Started:
1. Access MinIO console at http://localhost:9001
2. Login with the credentials from your .env file
3. Create buckets for different types of files
4. Upload and manage files through the console or API

## Integration Examples

### Example 1: Automated Document Processing

1. Use Maxun to extract data from scanned invoices
2. Store the original documents in MinIO
3. Use n8n to process the extracted data and update the database
4. Use Mastra AI to validate and categorize the documents

### Example 2: Predictive Maintenance

1. Use n8n to collect sensor data from HVAC equipment
2. Store the data in the PostgreSQL database
3. Use Mastra AI to analyze the data and predict maintenance needs
4. Generate service orders automatically when maintenance is needed

### Example 3: Customer Portal

1. Use the HVAC CRM/ERP system to manage customer information
2. Use MinIO to store customer documents
3. Use n8n to send notifications to customers
4. Use Mastra AI to provide personalized recommendations

## Troubleshooting

### Common Issues

1. **Services not starting**
   - Check Docker logs: `docker-compose -f docker-compose-full.yml logs`
   - Ensure ports are not already in use
   - Verify that the .env file has all required variables

2. **Database connection issues**
   - Check PostgreSQL logs: `docker-compose -f docker-compose-full.yml logs postgres`
   - Verify database credentials in .env file
   - Ensure the database is running: `docker ps | grep postgres`

3. **WebSocket connection errors**
   - Check Nginx logs: `docker-compose -f docker-compose-full.yml logs nginx`
   - Verify Nginx configuration
   - Ensure the services are running and accessible

4. **File storage issues**
   - Check MinIO logs: `docker-compose -f docker-compose-full.yml logs minio`
   - Verify MinIO credentials in .env file
   - Ensure the MinIO service is running: `docker ps | grep minio`

### Getting Help

If you encounter issues that are not covered in this document, please:
1. Check the logs of the specific service
2. Search the documentation of the specific service
3. Open an issue on the GitHub repository
4. Contact the development team

## Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Mastra AI Documentation](https://github.com/mastra-ai/mastra)
- [Maxun Documentation](https://github.com/getmaxun/maxun)
- [MinIO Documentation](https://min.io/docs/minio/container/index.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
