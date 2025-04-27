#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "Warning: Running as root is not recommended. Consider using a non-root user."
fi

# Set environment variables
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Check if we're running in a Docker container
if [ -f /.dockerenv ]; then
  echo "Running in Docker container"
  DOCKER_ENV=true
else
  DOCKER_ENV=false
fi

# Create necessary directories
mkdir -p logs
mkdir -p static
mkdir -p .streamlit

# Check for updates to dependencies
echo "Checking for updates to dependencies..."
python check_updates.py || echo "Update check failed, continuing anyway"

# Run health check
echo "Running health check..."
python -c "from utils.health_check import write_health_check_file; write_health_check_file()"

# Start the application
echo "Starting application in production mode..."
if [ "$DOCKER_ENV" = true ]; then
  # In Docker, run directly
  exec streamlit run app.py --server.headless=true --server.address=0.0.0.0 --server.port=8501
else
  # Outside Docker, use nohup to keep running after terminal closes
  nohup streamlit run app.py --server.headless=true --server.address=0.0.0.0 --server.port=8501 > logs/streamlit.log 2>&1 &
  echo "Application started in background. Check logs/streamlit.log for output."
  echo "To stop the application, run: pkill -f streamlit"
fi
