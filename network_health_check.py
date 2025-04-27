#!/usr/bin/env python
"""
Network Health Check Script

This script checks the network configuration and connectivity for the HVAC CRM/ERP system.
It verifies that the application is properly configured for networking.
"""

import os
import sys
import socket
import json
import logging
import argparse
import time
import asyncio
import websockets
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import networking configuration
try:
    from networking_config import load_config, get_websocket_url, get_local_ip
except ImportError:
    logger.error("Error: networking_config.py not found. Make sure it's in the current directory.")
    sys.exit(1)

def check_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Error checking port {port} on {host}: {e}")
        return False

def check_local_ports(config: Dict[str, Any]) -> List[Tuple[int, bool]]:
    """Check if local ports are open."""
    ports_to_check = [config.get("http_port", 8080)]
    results = []
    
    for port in ports_to_check:
        is_open = check_port_open("127.0.0.1", port)
        results.append((port, is_open))
    
    return results

async def check_websocket(url: str, timeout: float = 5.0) -> bool:
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

def check_dns_resolution(domain: str) -> bool:
    """Check if a domain can be resolved."""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def print_results(config: Dict[str, Any], local_ports: List[Tuple[int, bool]], 
                 websocket_result: bool, dns_result: bool) -> None:
    """Print health check results."""
    print("\n=== Network Health Check Results ===")
    
    # Local ports
    print("\nLocal Ports:")
    for port, is_open in local_ports:
        status = "OPEN" if is_open else "CLOSED"
        print(f"  Port {port}: {status}")
    
    # WebSocket
    print("\nWebSocket:")
    websocket_url = get_websocket_url(config)
    status = "WORKING" if websocket_result else "NOT WORKING"
    print(f"  URL: {websocket_url}")
    print(f"  Status: {status}")
    
    # DNS Resolution
    print("\nDNS Resolution:")
    domain = config.get("public_domain", "localhost")
    status = "OK" if dns_result else "FAILED"
    print(f"  Domain: {domain}")
    print(f"  Status: {status}")
    
    # Overall Status
    all_ports_open = all(is_open for _, is_open in local_ports)
    overall_status = "HEALTHY" if (all_ports_open and websocket_result and dns_result) else "UNHEALTHY"
    print(f"\nOverall Status: {overall_status}")
    
    print("===================================\n")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check network health")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout for checks in seconds")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Check local ports
    local_ports = check_local_ports(config)
    
    # Check WebSocket
    websocket_url = get_websocket_url(config)
    websocket_result = await check_websocket(websocket_url, args.timeout)
    
    # Check DNS resolution
    domain = config.get("public_domain", "localhost")
    dns_result = check_dns_resolution(domain)
    
    # Print results
    print_results(config, local_ports, websocket_result, dns_result)
    
    # Exit with appropriate status code
    all_ports_open = all(is_open for _, is_open in local_ports)
    if all_ports_open and websocket_result and dns_result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
