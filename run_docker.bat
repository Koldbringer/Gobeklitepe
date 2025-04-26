@echo off
echo Building and running HVAC CRM/ERP application in Docker...

docker build -t hvac-crm-erp .
docker run -p 8501:8501 hvac-crm-erp

echo The application is now running at http://localhost:8501
