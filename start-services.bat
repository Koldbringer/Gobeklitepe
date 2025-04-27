@echo off
echo Starting all services using Docker Compose...
docker-compose -f docker-compose-full.yml up -d

echo Waiting for services to start...
timeout /t 10 /nobreak > nul

echo.
docker-compose -f docker-compose-full.yml ps

echo.
echo Services are now available at:
echo - HVAC CRM/ERP: http://localhost:8501
echo - n8n Workflow Automation: http://localhost:5678
echo - Mastra AI Agent Framework: http://localhost:3000
echo - Maxun Web Data Extraction (Frontend): http://localhost:5173
echo - Maxun Web Data Extraction (Backend): http://localhost:8080
echo - MinIO Object Storage: http://localhost:9001
echo.
echo Or via Nginx at:
echo - HVAC CRM/ERP: https://hvac-crm.example.com
echo - n8n Workflow Automation: https://hvac-crm.example.com/n8n/
echo - Mastra AI Agent Framework: https://hvac-crm.example.com/mastra/
echo - Maxun Web Data Extraction: https://hvac-crm.example.com/maxun/
echo - Maxun Web Data Extraction API: https://hvac-crm.example.com/maxun-api/
echo - MinIO Object Storage: https://hvac-crm.example.com/minio/
