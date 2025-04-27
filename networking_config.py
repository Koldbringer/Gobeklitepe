"""
Networking Configuration for HVAC CRM/ERP System

This module provides configuration and utilities for networking settings,
including port configuration, WebSocket support, and domain settings.
"""

import os
import logging
import socket
import json
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "http_port": 8080,
    "websocket_enabled": True,
    "websocket_compression": False,
    "public_domain": "gobeklitepe-5hzle.kinsta.app",
    "public_port": 443,
    "public_protocol": "https",
    "private_hostname": "gobeklitepe-5hzle-web.gobeklitepe-5hzle.svc.cluster.local",
    "enable_cors": True,
    "allowed_origins": ["*"],
    "ip_restrictions": [],
    "cdn_enabled": True,
    "edge_caching_enabled": True,
    "grpc_enabled": True,
    "grpc_address": "0.0.0.0",
    "grpc_port": 8080,
    "grpc_max_workers": 10,
    "grpc_reflection_enabled": True,
    "grpc_compression": False,
    "grpc_ssl_enabled": False
}

# Configuration file path
CONFIG_FILE = "networking.json"

def load_config() -> Dict[str, Any]:
    """Load networking configuration from file or environment variables."""
    config = DEFAULT_CONFIG.copy()

    # Try to load from config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
                logger.info(f"Loaded networking configuration from {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error loading configuration from {CONFIG_FILE}: {e}")

    # Override with environment variables
    env_mapping = {
        "PORT": "http_port",
        "STREAMLIT_SERVER_PORT": "http_port",
        "STREAMLIT_SERVER_ADDRESS": "http_address",
        "STREAMLIT_SERVER_HEADLESS": "headless",
        "STREAMLIT_SERVER_ENABLE_CORS": "enable_cors",
        "STREAMLIT_SERVER_ENABLEXSRFPROTECTION": "enable_xsrf_protection",
        "STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION": "websocket_compression",
        "STREAMLIT_BROWSER_SERVERADDRESS": "public_domain",
        "STREAMLIT_BROWSER_SERVERPORT": "public_port",
        "PUBLIC_DOMAIN": "public_domain",
        "PUBLIC_PORT": "public_port",
        "PUBLIC_PROTOCOL": "public_protocol",
        "PRIVATE_HOSTNAME": "private_hostname",
        "ALLOWED_ORIGINS": "allowed_origins",
        "IP_RESTRICTIONS": "ip_restrictions",
        "CDN_ENABLED": "cdn_enabled",
        "EDGE_CACHING_ENABLED": "edge_caching_enabled",
        "GRPC_ENABLED": "grpc_enabled",
        "GRPC_ADDRESS": "grpc_address",
        "GRPC_PORT": "grpc_port",
        "GRPC_MAX_WORKERS": "grpc_max_workers",
        "GRPC_REFLECTION_ENABLED": "grpc_reflection_enabled",
        "GRPC_COMPRESSION": "grpc_compression",
        "GRPC_SSL_ENABLED": "grpc_ssl_enabled"
    }

    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]

            # Convert boolean strings
            if value.lower() in ("true", "yes", "1"):
                value = True
            elif value.lower() in ("false", "no", "0"):
                value = False
            # Convert numeric strings
            elif value.isdigit():
                value = int(value)
            # Convert JSON strings for lists and dicts
            elif value.startswith("[") or value.startswith("{"):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            config[config_key] = value
            logger.debug(f"Set {config_key}={value} from environment variable {env_var}")

    return config

def save_config(config: Dict[str, Any]) -> bool:
    """Save networking configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved networking configuration to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {CONFIG_FILE}: {e}")
        return False

def get_local_ip() -> str:
    """Get the local IP address of the machine."""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_websocket_url(config: Optional[Dict[str, Any]] = None) -> str:
    """Get the WebSocket URL based on the current configuration."""
    if config is None:
        config = load_config()

    protocol = "wss" if config.get("public_protocol", "https") == "https" else "ws"
    domain = config.get("public_domain", "localhost")
    port = config.get("public_port", 443)

    # Don't include standard ports in the URL
    if (protocol == "ws" and port == 80) or (protocol == "wss" and port == 443):
        return f"{protocol}://{domain}/_stcore/stream"
    else:
        return f"{protocol}://{domain}:{port}/_stcore/stream"

def get_streamlit_config() -> Dict[str, Any]:
    """Get Streamlit configuration based on networking settings."""
    config = load_config()

    streamlit_config = {
        "server.port": config.get("http_port", 8080),
        "server.address": config.get("http_address", "0.0.0.0"),
        "server.headless": config.get("headless", True),
        "server.enableCORS": config.get("enable_cors", True),
        "server.enableXsrfProtection": config.get("enable_xsrf_protection", False),
        "server.enableWebsocketCompression": config.get("websocket_compression", False),
        "browser.serverAddress": config.get("public_domain", "localhost"),
        "browser.serverPort": config.get("public_port", 443),
    }

    return streamlit_config

def get_grpc_url(config: Optional[Dict[str, Any]] = None) -> str:
    """Get the gRPC URL based on the current configuration."""
    if config is None:
        config = load_config()

    address = config.get("grpc_address", "0.0.0.0")
    port = config.get("grpc_port", 8080)

    return f"grpc://{address}:{port}"

def print_network_info() -> None:
    """Print networking information for debugging."""
    config = load_config()
    local_ip = get_local_ip()
    websocket_url = get_websocket_url(config)
    grpc_url = get_grpc_url(config)

    print("\n=== Networking Configuration ===")
    print(f"Local IP: {local_ip}")

    # HTTP information
    print(f"\nHTTP Configuration:")
    print(f"  Port: {config.get('http_port', 8080)}")
    print(f"  Public Domain: {config.get('public_domain', 'localhost')}")
    print(f"  Public URL: {config.get('public_protocol', 'https')}://{config.get('public_domain', 'localhost')}")

    # WebSocket information
    print(f"\nWebSocket Configuration:")
    print(f"  Enabled: {config.get('websocket_enabled', True)}")
    print(f"  URL: {websocket_url}")
    print(f"  Compression: {config.get('websocket_compression', False)}")

    # gRPC information
    print(f"\ngRPC Configuration:")
    print(f"  Enabled: {config.get('grpc_enabled', True)}")
    print(f"  URL: {grpc_url}")
    print(f"  Max Workers: {config.get('grpc_max_workers', 10)}")
    print(f"  Reflection Enabled: {config.get('grpc_reflection_enabled', True)}")
    print(f"  Compression: {config.get('grpc_compression', False)}")
    print(f"  SSL Enabled: {config.get('grpc_ssl_enabled', False)}")

    # Other information
    print(f"\nOther Configuration:")
    print(f"  Private Hostname: {config.get('private_hostname', '')}")
    print(f"  CORS Enabled: {config.get('enable_cors', True)}")
    print(f"  CDN Enabled: {config.get('cdn_enabled', True)}")
    print(f"  Edge Caching Enabled: {config.get('edge_caching_enabled', True)}")

    print("================================\n")

if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(level=logging.INFO)

    # Print current configuration
    config = load_config()
    print(json.dumps(config, indent=2))

    # Print network info
    print_network_info()
