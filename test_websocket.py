import asyncio
import websockets
import logging
import sys
import json
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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

async def main():
    """Main function to test WebSocket connections."""
    parser = argparse.ArgumentParser(description='Test WebSocket connections')
    parser.add_argument('--url', type=str, default='ws://localhost:8080/_stcore/stream',
                        help='WebSocket URL to test')
    parser.add_argument('--timeout', type=int, default=10,
                        help='Timeout in seconds for WebSocket operations')
    args = parser.parse_args()
    
    # Test the WebSocket connection
    success = await test_websocket(args.url, args.timeout)
    
    # Exit with appropriate status code
    if success:
        logger.info("WebSocket test successful")
        sys.exit(0)
    else:
        logger.error("WebSocket test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
