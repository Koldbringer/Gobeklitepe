#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8080}

# Print environment information
echo "Starting application with the following configuration:"
echo "PORT: $PORT"
echo "Current directory: $(pwd)"

# Check for any existing WebSocket test lock files and remove them
if [ -f "websocket_test.lock" ]; then
    echo "Removing existing WebSocket test lock file..."
    rm -f websocket_test.lock
fi

# Set Streamlit environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
export STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=false

# Generate the WebSocket test HTML file
echo "Generating WebSocket test file..."
python consolidated_websocket_test.py --generate-html --url "ws://localhost:$PORT/_stcore/stream"

# Start the application
echo "Starting Streamlit application on port $PORT..."
exec streamlit run app.py
