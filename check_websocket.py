import asyncio
import websockets
import logging
import sys
import json
import argparse
import requests
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

async def check_websocket(url, timeout=10):
    """Check if a WebSocket server is running at the given URL."""
    logger.info(f"Checking WebSocket connection to {url}")
    try:
        async with websockets.connect(url, ping_interval=None, close_timeout=timeout) as websocket:
            logger.info(f"Successfully connected to WebSocket at {url}")
            await websocket.send("Hello, WebSocket!")
            logger.info(f"Message sent to {url}")
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            logger.info(f"Received response: {response}")
            return True
    except Exception as e:
        logger.error(f"Failed to connect to WebSocket at {url}: {e}")
        return False

def check_http(url):
    """Check if an HTTP server is running at the given URL."""
    logger.info(f"Checking HTTP connection to {url}")
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"HTTP response status code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to connect to HTTP server at {url}: {e}")
        return False

async def main():
    """Check WebSocket connections to various endpoints."""
    parser = argparse.ArgumentParser(description='Check WebSocket connections')
    parser.add_argument('--host', type=str, default='gobeklitepe-5hzle.kinsta.app',
                        help='Host to check')
    parser.add_argument('--secure', action='store_true',
                        help='Use secure connections (wss/https)')
    args = parser.parse_args()
    
    # Determine protocol
    ws_protocol = "wss" if args.secure else "ws"
    http_protocol = "https" if args.secure else "http"
    
    # Check HTTP connection
    http_url = f"{http_protocol}://{args.host}"
    http_success = check_http(http_url)
    
    # Check WebSocket connections
    ws_endpoints = [
        f"{ws_protocol}://{args.host}/_stcore/stream",
        f"{ws_protocol}://{args.host}/stream"
    ]
    
    ws_results = []
    for endpoint in ws_endpoints:
        result = await check_websocket(endpoint)
        ws_results.append((endpoint, result))
    
    # Print summary
    logger.info("Connection Check Results:")
    logger.info(f"HTTP ({http_url}): {'SUCCESS' if http_success else 'FAILED'}")
    
    for endpoint, result in ws_results:
        status = "SUCCESS" if result else "FAILED"
        logger.info(f"WebSocket ({endpoint}): {status}")
    
    # Exit with error code if all checks failed
    if not http_success and not any(result for _, result in ws_results):
        logger.error("All connection checks failed")
        sys.exit(1)
    
    if not any(result for _, result in ws_results):
        logger.error("All WebSocket connection checks failed")
        sys.exit(1)
    
    logger.info("At least one connection is working")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
