@echo off
echo Stopping all services...
docker-compose -f docker-compose-full.yml down

echo.
echo All services have been stopped.
