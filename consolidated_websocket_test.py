#!/usr/bin/env python
"""
Consolidated WebSocket Test Script for HVAC CRM/ERP System

This script provides a unified way to test WebSocket connections for the application.
It handles both server-side testing and client-side HTML test page generation.
"""

import asyncio
import websockets
import logging
import sys
import json
import argparse
import os
import signal
import time
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global flag to track if the script is already running
LOCK_FILE = "websocket_test.lock"

def check_already_running():
    """Check if another instance of this script is already running."""
    if os.path.exists(LOCK_FILE):
        # Check if the process is still running
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Try to send signal 0 to the process (doesn't actually send a signal,
            # but checks if the process exists)
            try:
                os.kill(pid, 0)
                logger.error(f"Another instance is already running with PID {pid}")
                return True
            except OSError:
                # Process doesn't exist, so we can remove the lock file
                logger.warning(f"Removing stale lock file for PID {pid}")
                os.remove(LOCK_FILE)
                return False
        except (ValueError, IOError):
            # Invalid PID or can't read the file
            logger.warning("Removing invalid lock file")
            os.remove(LOCK_FILE)
            return False
    return False

def create_lock_file():
    """Create a lock file with the current process ID."""
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def remove_lock_file():
    """Remove the lock file."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def cleanup_handler(signum, frame):
    """Handle cleanup when the script is terminated."""
    logger.info("Cleaning up before exit...")
    remove_lock_file()
    sys.exit(0)

async def test_websocket(url, timeout=10):
    """Test a WebSocket connection to the specified URL."""
    logger.info(f"Testing WebSocket connection to {url}")
    
    try:
        # Connect to the WebSocket server with a timeout
        async with websockets.connect(url, ping_interval=None, close_timeout=timeout) as websocket:
            logger.info(f"Successfully connected to WebSocket at {url}")
            
            # Send a test message
            test_message = json.dumps({
                "type": "test",
                "message": "Hello from WebSocket test script"
            })
            await websocket.send(test_message)
            logger.info(f"Sent test message: {test_message}")
            
            # Wait for a response with a timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                logger.info(f"Received response: {response}")
                
                # Try to parse the response as JSON
                try:
                    json_response = json.loads(response)
                    logger.info(f"Parsed JSON response: {json.dumps(json_response, indent=2)}")
                except json.JSONDecodeError:
                    logger.info("Response is not valid JSON")
                
                return True
            except asyncio.TimeoutError:
                logger.warning(f"No response received within {timeout} seconds")
                return False
    
    except Exception as e:
        logger.error(f"Error connecting to WebSocket at {url}: {e}")
        return False

def generate_test_html(output_file="websocket_test.html", default_url="ws://localhost:8080/_stcore/stream"):
    """Generate an HTML file for testing WebSocket connections."""
    logger.info(f"Generating WebSocket test HTML file: {output_file}")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .log {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .info {{ color: blue; }}
    </style>
</head>
<body>
    <h1>WebSocket Test for Streamlit</h1>
    
    <div>
        <label for="wsUrl">WebSocket URL:</label>
        <input type="text" id="wsUrl" value="{default_url}" style="width: 400px;">
        <button onclick="testWebSocket()">Test Connection</button>
    </div>
    
    <h2>Connection Log:</h2>
    <div id="log" class="log"></div>
    
    <script>
        function log(message, type = 'info') {{
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = type;
            entry.textContent = new Date().toISOString() + ': ' + message;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }}
        
        function testWebSocket() {{
            const wsUrl = document.getElementById('wsUrl').value;
            log('Testing connection to: ' + wsUrl);
            
            try {{
                const ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {{
                    log('WebSocket connection established successfully!', 'success');
                    // Try to send a message
                    try {{
                        ws.send('Hello from WebSocket test');
                        log('Test message sent', 'success');
                    }} catch (e) {{
                        log('Error sending message: ' + e.message, 'error');
                    }}
                }};
                
                ws.onmessage = function(event) {{
                    log('Received message: ' + event.data, 'success');
                    // Try to parse the message as JSON
                    try {{
                        const data = JSON.parse(event.data);
                        log('Parsed JSON: ' + JSON.stringify(data, null, 2), 'info');
                    }} catch (e) {{
                        log('Message is not JSON: ' + e.message, 'info');
                    }}
                }};
                
                ws.onerror = function(error) {{
                    log('WebSocket error: ' + JSON.stringify(error), 'error');
                }};
                
                ws.onclose = function(event) {{
                    log('WebSocket connection closed. Code: ' + event.code + ', Reason: ' + event.reason, 'info');
                }};
            }} catch (e) {{
                log('Error creating WebSocket: ' + e.message, 'error');
            }}
        }}
        
        // Automatically test the connection when the page loads
        window.onload = function() {{
            // Wait a second before testing to ensure the page is fully loaded
            setTimeout(testWebSocket, 1000);
        }};
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"WebSocket test HTML file generated: {output_file}")
    return output_file

async def main():
    """Main function to test WebSocket connections."""
    # Register signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    # Check if another instance is already running
    if check_already_running():
        logger.error("Another instance of this script is already running. Exiting.")
        sys.exit(1)
    
    # Create lock file
    create_lock_file()
    
    try:
        parser = argparse.ArgumentParser(description='Test WebSocket connections')
        parser.add_argument('--url', type=str, default='ws://localhost:8080/_stcore/stream',
                            help='WebSocket URL to test')
        parser.add_argument('--timeout', type=int, default=10,
                            help='Timeout in seconds for WebSocket operations')
        parser.add_argument('--generate-html', action='store_true',
                            help='Generate HTML test page')
        parser.add_argument('--html-output', type=str, default='websocket_test.html',
                            help='Output file for HTML test page')
        args = parser.parse_args()
        
        # Generate HTML test page if requested
        if args.generate_html:
            generate_test_html(args.html_output, args.url)
        
        # Test the WebSocket connection
        success = await test_websocket(args.url, args.timeout)
        
        # Exit with appropriate status code
        if success:
            logger.info("WebSocket test successful")
            sys.exit(0)
        else:
            logger.error("WebSocket test failed")
            sys.exit(1)
    
    finally:
        # Always remove the lock file when done
        remove_lock_file()

if __name__ == "__main__":
    asyncio.run(main())
