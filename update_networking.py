#!/usr/bin/env python
"""
Update Networking Configuration Script

This script allows updating the networking configuration for the HVAC CRM/ERP system.
It provides a command-line interface to modify networking settings.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

# Import networking configuration module
try:
    from networking_config import load_config, save_config, print_network_info
except ImportError:
    print("Error: networking_config.py not found. Make sure it's in the current directory.")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Update networking configuration")
    
    # HTTP configuration
    parser.add_argument("--http-port", type=int, help="HTTP port for the application")
    parser.add_argument("--http-address", help="HTTP address to bind to")
    
    # Public access configuration
    parser.add_argument("--public-domain", help="Public domain name")
    parser.add_argument("--public-port", type=int, help="Public port")
    parser.add_argument("--public-protocol", choices=["http", "https"], help="Public protocol (http or https)")
    
    # Private networking configuration
    parser.add_argument("--private-hostname", help="Private hostname for internal access")
    
    # WebSocket configuration
    parser.add_argument("--websocket-enabled", type=bool, help="Enable WebSocket support")
    parser.add_argument("--websocket-compression", type=bool, help="Enable WebSocket compression")
    
    # Security configuration
    parser.add_argument("--enable-cors", type=bool, help="Enable CORS")
    parser.add_argument("--allowed-origins", help="Comma-separated list of allowed origins for CORS")
    parser.add_argument("--add-ip-restriction", help="Add IP restriction (CIDR format)")
    parser.add_argument("--remove-ip-restriction", help="Remove IP restriction (CIDR format)")
    parser.add_argument("--clear-ip-restrictions", action="store_true", help="Clear all IP restrictions")
    
    # CDN configuration
    parser.add_argument("--cdn-enabled", type=bool, help="Enable CDN")
    parser.add_argument("--edge-caching-enabled", type=bool, help="Enable edge caching")
    
    # Other options
    parser.add_argument("--print", action="store_true", help="Print current configuration")
    parser.add_argument("--reset", action="store_true", help="Reset to default configuration")
    
    return parser.parse_args()

def update_config(args, config: Dict[str, Any]) -> Dict[str, Any]:
    """Update configuration based on command line arguments."""
    # HTTP configuration
    if args.http_port is not None:
        config["http_port"] = args.http_port
    if args.http_address is not None:
        config["http_address"] = args.http_address
    
    # Public access configuration
    if args.public_domain is not None:
        config["public_domain"] = args.public_domain
    if args.public_port is not None:
        config["public_port"] = args.public_port
    if args.public_protocol is not None:
        config["public_protocol"] = args.public_protocol
    
    # Private networking configuration
    if args.private_hostname is not None:
        config["private_hostname"] = args.private_hostname
    
    # WebSocket configuration
    if args.websocket_enabled is not None:
        config["websocket_enabled"] = args.websocket_enabled
    if args.websocket_compression is not None:
        config["websocket_compression"] = args.websocket_compression
    
    # Security configuration
    if args.enable_cors is not None:
        config["enable_cors"] = args.enable_cors
    if args.allowed_origins is not None:
        config["allowed_origins"] = args.allowed_origins.split(",")
    
    # IP restrictions
    if args.clear_ip_restrictions:
        config["ip_restrictions"] = []
    if args.add_ip_restriction:
        if "ip_restrictions" not in config:
            config["ip_restrictions"] = []
        if args.add_ip_restriction not in config["ip_restrictions"]:
            config["ip_restrictions"].append(args.add_ip_restriction)
    if args.remove_ip_restriction and "ip_restrictions" in config:
        if args.remove_ip_restriction in config["ip_restrictions"]:
            config["ip_restrictions"].remove(args.remove_ip_restriction)
    
    # CDN configuration
    if args.cdn_enabled is not None:
        config["cdn_enabled"] = args.cdn_enabled
    if args.edge_caching_enabled is not None:
        config["edge_caching_enabled"] = args.edge_caching_enabled
    
    return config

def main():
    """Main function."""
    args = parse_args()
    
    # Load current configuration
    config = load_config()
    
    # Reset to default if requested
    if args.reset:
        from networking_config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.copy()
        print("Configuration reset to defaults.")
    
    # Update configuration based on arguments
    config = update_config(args, config)
    
    # Save updated configuration
    save_config(config)
    
    # Print configuration if requested
    if args.print:
        print(json.dumps(config, indent=2))
        print_network_info()
    
    print("Networking configuration updated successfully.")

if __name__ == "__main__":
    main()
