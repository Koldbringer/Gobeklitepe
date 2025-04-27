#!/usr/bin/env python
"""
TCP Proxy Test Script

This script tests TCP proxy connections for the HVAC CRM/ERP system.
It can be used to verify that TCP proxying is working correctly.
"""

import socket
import sys
import time
import argparse
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_tcp_server(host: str = '0.0.0.0', port: int = 9000) -> Optional[socket.socket]:
    """Create a TCP server socket."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        logger.info(f"TCP server listening on {host}:{port}")
        return server_socket
    except Exception as e:
        logger.error(f"Error creating TCP server: {e}")
        return None

def accept_connection(server_socket: socket.socket, timeout: float = 30.0) -> Tuple[Optional[socket.socket], Optional[Tuple[str, int]]]:
    """Accept a connection on the server socket with timeout."""
    try:
        server_socket.settimeout(timeout)
        client_socket, client_address = server_socket.accept()
        logger.info(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        return client_socket, client_address
    except socket.timeout:
        logger.warning(f"Timeout waiting for connection after {timeout} seconds")
        return None, None
    except Exception as e:
        logger.error(f"Error accepting connection: {e}")
        return None, None

def handle_client(client_socket: socket.socket) -> None:
    """Handle a client connection."""
    try:
        # Send a welcome message
        welcome_message = "Welcome to the HVAC CRM/ERP TCP Proxy Test Server\r\n"
        client_socket.send(welcome_message.encode())
        
        # Set a timeout for receiving data
        client_socket.settimeout(10.0)
        
        # Receive and echo data
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    logger.info("Client closed connection")
                    break
                
                logger.info(f"Received: {data.decode().strip()}")
                
                # Echo the data back with a prefix
                response = f"ECHO: {data.decode()}"
                client_socket.send(response.encode())
            except socket.timeout:
                logger.info("Timeout waiting for data, sending keepalive")
                client_socket.send(b"KEEPALIVE\r\n")
            except Exception as e:
                logger.error(f"Error receiving data: {e}")
                break
    finally:
        client_socket.close()

def create_tcp_client(host: str, port: int, timeout: float = 5.0) -> Optional[socket.socket]:
    """Create a TCP client socket and connect to server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        logger.info(f"Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        logger.info(f"Connected to {host}:{port}")
        return client_socket
    except Exception as e:
        logger.error(f"Error connecting to {host}:{port}: {e}")
        return None

def test_tcp_client(host: str, port: int, messages: int = 3, delay: float = 1.0) -> bool:
    """Test TCP client connection by sending messages."""
    client_socket = create_tcp_client(host, port)
    if not client_socket:
        return False
    
    try:
        # Receive welcome message
        welcome = client_socket.recv(1024)
        logger.info(f"Received: {welcome.decode().strip()}")
        
        # Send test messages
        for i in range(messages):
            message = f"Test message {i+1}\r\n"
            logger.info(f"Sending: {message.strip()}")
            client_socket.send(message.encode())
            
            # Receive response
            response = client_socket.recv(1024)
            logger.info(f"Received: {response.decode().strip()}")
            
            # Wait before sending next message
            if i < messages - 1:
                time.sleep(delay)
        
        return True
    except Exception as e:
        logger.error(f"Error in TCP client test: {e}")
        return False
    finally:
        client_socket.close()

def run_server(host: str, port: int, timeout: float = 60.0) -> None:
    """Run a TCP server that echoes messages."""
    server_socket = create_tcp_server(host, port)
    if not server_socket:
        return
    
    try:
        logger.info(f"TCP server running on {host}:{port}")
        logger.info(f"Waiting for connections (timeout: {timeout} seconds)...")
        
        client_socket, client_address = accept_connection(server_socket, timeout)
        if client_socket:
            handle_client(client_socket)
    finally:
        server_socket.close()
        logger.info("TCP server stopped")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test TCP proxy connections")
    parser.add_argument("--mode", choices=["server", "client"], default="server",
                        help="Mode to run in (server or client)")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to bind to (server) or connect to (client)")
    parser.add_argument("--port", type=int, default=9000,
                        help="Port to use")
    parser.add_argument("--timeout", type=float, default=60.0,
                        help="Timeout in seconds")
    parser.add_argument("--messages", type=int, default=3,
                        help="Number of messages to send (client mode)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between messages in seconds (client mode)")
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.host, args.port, args.timeout)
    else:
        success = test_tcp_client(args.host, args.port, args.messages, args.delay)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
