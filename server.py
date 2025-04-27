import os
import sys
import http.server
import socketserver
import threading
import time
import logging
import subprocess
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """Simple HTTP request handler with GET and HEAD commands."""
    
    def do_GET(self):
        """Serve a GET request."""
        parsed_path = urlparse(self.path)
        
        # Serve health check page
        if parsed_path.path == '/health' or parsed_path.path == '/health.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            try:
                with open('health.html', 'rb') as file:
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.wfile.write(b"<html><body><h1>Health Check</h1><p>Server is running, but health.html not found.</p></body></html>")
            return
        
        # Serve WebSocket test page
        elif parsed_path.path == '/websocket-test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WebSocket Test</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .log { background-color: #f8f9fa; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }
                    .success { color: green; }
                    .error { color: red; }
                </style>
            </head>
            <body>
                <h1>WebSocket Test</h1>
                <div>
                    <label for="wsUrl">WebSocket URL:</label>
                    <input type="text" id="wsUrl" value="wss://gobeklitepe-5hzle.kinsta.app/_stcore/stream" style="width: 400px;">
                    <button onclick="testWebSocket()">Test Connection</button>
                </div>
                <h2>Connection Log:</h2>
                <div id="log" class="log"></div>
                
                <script>
                    function log(message, isError) {
                        const logDiv = document.getElementById('log');
                        const entry = document.createElement('div');
                        entry.className = isError ? 'error' : 'success';
                        entry.textContent = new Date().toISOString() + ': ' + message;
                        logDiv.appendChild(entry);
                        logDiv.scrollTop = logDiv.scrollHeight;
                    }
                    
                    function testWebSocket() {
                        const wsUrl = document.getElementById('wsUrl').value;
                        log('Testing connection to: ' + wsUrl);
                        
                        try {
                            const ws = new WebSocket(wsUrl);
                            
                            ws.onopen = function() {
                                log('WebSocket connection established successfully!');
                                // Try to send a message
                                try {
                                    ws.send('Hello from WebSocket test');
                                    log('Test message sent');
                                } catch (e) {
                                    log('Error sending message: ' + e.message, true);
                                }
                            };
                            
                            ws.onmessage = function(event) {
                                log('Received message: ' + event.data);
                            };
                            
                            ws.onerror = function(error) {
                                log('WebSocket error: ' + JSON.stringify(error), true);
                            };
                            
                            ws.onclose = function(event) {
                                log('WebSocket connection closed. Code: ' + event.code + ', Reason: ' + event.reason);
                            };
                        } catch (e) {
                            log('Error creating WebSocket: ' + e.message, true);
                        }
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        # Default: redirect to health check
        else:
            self.send_response(302)
            self.send_header('Location', '/health')
            self.end_headers()
            return

    def log_message(self, format, *args):
        """Log an arbitrary message."""
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

def run_health_server(port=8000):
    """Run a simple HTTP server for health checks."""
    try:
        handler = HealthCheckHandler
        httpd = socketserver.TCPServer(("", port), handler)
        logger.info(f"Starting health check server on port {port}")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health check server: {e}")

def main():
    """Main function to start the health check server."""
    # Start health check server in a separate thread
    health_port = int(os.environ.get('HEALTH_PORT', 8000))
    health_thread = threading.Thread(target=run_health_server, args=(health_port,), daemon=True)
    health_thread.start()
    
    logger.info(f"Health check server started on port {health_port}")
    logger.info(f"Access health check at: http://localhost:{health_port}/health")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)

if __name__ == "__main__":
    main()
