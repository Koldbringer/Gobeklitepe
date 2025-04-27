import asyncio
import websockets
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_websocket(url):
    """Check if a WebSocket server is running at the given URL."""
    logger.info(f"Checking WebSocket connection to {url}")
    try:
        async with websockets.connect(url, ping_interval=None) as websocket:
            logger.info(f"Successfully connected to WebSocket at {url}")
            await websocket.send("Hello, WebSocket!")
            logger.info(f"Message sent to {url}")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            logger.info(f"Received response: {response}")
            return True
    except Exception as e:
        logger.error(f"Failed to connect to WebSocket at {url}: {e}")
        return False

async def main():
    """Check WebSocket connections to various endpoints."""
    # Get the host from environment or use default
    host = os.environ.get("WEBSOCKET_CHECK_HOST", "localhost")
    port = os.environ.get("WEBSOCKET_CHECK_PORT", "8080")
    
    # Check both the legacy and new WebSocket endpoints
    endpoints = [
        f"ws://{host}:{port}/_stcore/stream",
        f"ws://{host}:{port}/stream"
    ]
    
    results = []
    for endpoint in endpoints:
        result = await check_websocket(endpoint)
        results.append((endpoint, result))
    
    # Print summary
    logger.info("WebSocket Connection Check Results:")
    for endpoint, result in results:
        status = "SUCCESS" if result else "FAILED"
        logger.info(f"{endpoint}: {status}")
    
    # Exit with error code if all checks failed
    if not any(result for _, result in results):
        logger.error("All WebSocket connection checks failed")
        sys.exit(1)
    
    logger.info("At least one WebSocket endpoint is working")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
