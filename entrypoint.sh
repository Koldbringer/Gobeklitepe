#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8080}

# Print environment information for debugging
echo "Starting application with the following configuration:"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Skip database check in production environment
if [ "$SKIP_DB_CHECK" = "true" ]; then
    echo "Skipping database connection check as SKIP_DB_CHECK=true"
else
    # Check if database connection is available (but don't fail if it's not)
    echo "Checking database connection..."
    python -c "
import sys
import time
import os
try:
    import psycopg2
    from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

    print(f'Database config: {DB_HOST}:{DB_PORT}/{DB_NAME}')

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            conn.close()
            print('Database connection successful!')
            break
        except Exception as e:
            retry_count += 1
            print(f'Database connection attempt {retry_count}/{max_retries} failed: {e}')
            if retry_count < max_retries:
                time.sleep(2)

    # Continue even if database connection fails
    if retry_count >= max_retries:
        print('Could not connect to database after multiple attempts')
        print('Continuing anyway to allow application to start...')
except ImportError as e:
    print(f'Import error: {e}')
    print('Continuing without database connection check...')
except Exception as e:
    print(f'Unexpected error during database check: {e}')
    print('Continuing anyway to allow application to start...')
"
fi

# Set default values for networking configuration
export PORT=${PORT:-8080}
export PUBLIC_DOMAIN=${PUBLIC_DOMAIN:-"gobeklitepe-5hzle.kinsta.app"}
export PUBLIC_PORT=${PUBLIC_PORT:-443}
export PUBLIC_PROTOCOL=${PUBLIC_PROTOCOL:-"https"}
export PRIVATE_HOSTNAME=${PRIVATE_HOSTNAME:-"gobeklitepe-5hzle-web.gobeklitepe-5hzle.svc.cluster.local"}

# Make sure the port is properly set for Streamlit
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
export STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=false
export STREAMLIT_BROWSER_SERVERADDRESS="$PUBLIC_DOMAIN"
export STREAMLIT_BROWSER_SERVERPORT=$PUBLIC_PORT

# Generate networking configuration
echo "Generating networking configuration..."
python networking_config.py

# Generate the WebSocket test HTML file
# Always ensure correct ws/wss scheme
if [ "$PUBLIC_PROTOCOL" = "https" ]; then
  WS_URL="wss://${PUBLIC_DOMAIN}/_stcore/stream"
else
  WS_URL="ws://${PUBLIC_DOMAIN}/_stcore/stream"
fi

echo "Generating WebSocket test file..."
python consolidated_websocket_test.py --generate-html --url "$WS_URL"

# Create a simple health check file
echo "Creating health check file..."
cat > health.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>HVAC CRM/ERP Health Check</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .ok { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>HVAC CRM/ERP System Health Check</h1>
    <div class="status ok">
        <h2>Server Status: OK</h2>
        <p>The server is running and responding to requests.</p>
        <p>Timestamp: $(date)</p>
    </div>
    <div>
        <h3>Environment Information:</h3>
        <ul>
            <li>PORT: $PORT</li>
            <li>STREAMLIT_SERVER_PORT: $STREAMLIT_SERVER_PORT</li>
            <li>STREAMLIT_SERVER_ADDRESS: $STREAMLIT_SERVER_ADDRESS</li>
            <li>STREAMLIT_BROWSER_SERVERADDRESS: $STREAMLIT_BROWSER_SERVERADDRESS</li>
            <li>STREAMLIT_BROWSER_SERVERPORT: $STREAMLIT_BROWSER_SERVERPORT</li>
            <li>HOSTNAME: $(hostname)</li>
        </ul>
    </div>
    <div>
        <h3>WebSocket Test:</h3>
        <p>You can test WebSocket connections using the <a href="/websocket_test.html">WebSocket Test Page</a>.</p>
    </div>
    <script>
        // Simple WebSocket test
        function testWebSocket() {
            const wsUrl = window.location.protocol === 'https:'
                ? 'wss://' + window.location.host + '/_stcore/stream'
                : 'ws://' + window.location.host + '/_stcore/stream';

            const statusDiv = document.createElement('div');
            statusDiv.className = 'status';
            statusDiv.innerHTML = '<h2>WebSocket Test</h2><p>Testing connection to: ' + wsUrl + '</p>';
            document.body.appendChild(statusDiv);

            try {
                const ws = new WebSocket(wsUrl);

                ws.onopen = function() {
                    statusDiv.className = 'status ok';
                    statusDiv.innerHTML += '<p>WebSocket connection successful!</p>';
                };

                ws.onerror = function(error) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML += '<p>WebSocket connection failed.</p>';
                };

                ws.onclose = function() {
                    statusDiv.innerHTML += '<p>WebSocket connection closed.</p>';
                };
            } catch (e) {
                statusDiv.className = 'status error';
                statusDiv.innerHTML += '<p>Error creating WebSocket: ' + e.message + '</p>';
            }
        }

        // Run the test when the page loads
        window.onload = testWebSocket;
    </script>
</body>
</html>
EOF

# Create a simple server to serve the health check and WebSocket test files
echo "Creating simple HTTP server..."
cat > simple_server.py << EOF
import http.server
import socketserver
import threading
import time
import os

# Get the port from environment or use default
PORT = int(os.environ.get('HEALTH_PORT', 8000))

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def run_server():
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving health check on port {PORT}")
        httpd.serve_forever()

# Start the server in a separate thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print(f"Health check server started on port {PORT}")
EOF

# Start the health check server in the background
echo "Starting health check server..."
python simple_server.py &

# Start the application
echo "Starting Streamlit application on port $PORT..."
exec streamlit run app.py
