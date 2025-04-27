# Networking Configuration for HVAC CRM/ERP System

This document provides information on how to configure networking for the HVAC CRM/ERP system.

## Overview

The HVAC CRM/ERP system supports various networking configurations, including:

- HTTP/HTTPS access
- WebSocket connections for real-time updates
- CDN and edge caching
- IP restrictions
- Private networking

## Configuration Files

The networking configuration is stored in the following files:

- `networking.json`: Main configuration file
- `networking_config.py`: Python module for loading and saving configuration
- `update_networking.py`: Script for updating configuration
- `network_health_check.py`: Script for checking network health

## Quick Start

### Viewing Current Configuration

To view the current networking configuration:

```bash
python networking_config.py
```

Or use the batch file:

```bash
update_networking.bat
```

### Updating Configuration

To update the networking configuration, use the `update_networking.bat` script:

```bash
update_networking.bat --http-port 8080 --public-domain example.com
```

### Checking Network Health

To check the health of your network configuration:

```bash
check_network.bat
```

## Configuration Options

### HTTP Configuration

- `http_port`: Port for the HTTP server (default: 8080)
- `http_address`: Address to bind the HTTP server (default: 0.0.0.0)

### Public Access Configuration

- `public_domain`: Public domain name (default: gobeklitepe-5hzle.kinsta.app)
- `public_port`: Public port (default: 443)
- `public_protocol`: Public protocol (http or https, default: https)

### WebSocket Configuration

- `websocket_enabled`: Enable WebSocket support (default: true)
- `websocket_compression`: Enable WebSocket compression (default: false)

### Security Configuration

- `enable_cors`: Enable CORS (default: true)
- `allowed_origins`: List of allowed origins for CORS (default: ["*"])
- `ip_restrictions`: List of IP restrictions in CIDR format (default: [])

### CDN Configuration

- `cdn_enabled`: Enable CDN (default: true)
- `edge_caching_enabled`: Enable edge caching (default: true)

### Private Networking

- `private_hostname`: Private hostname for internal access (default: gobeklitepe-5hzle-web.gobeklitepe-5hzle.svc.cluster.local)

## Environment Variables

The following environment variables can be used to override configuration:

- `PORT`: HTTP port
- `PUBLIC_DOMAIN`: Public domain name
- `PUBLIC_PORT`: Public port
- `PUBLIC_PROTOCOL`: Public protocol (http or https)
- `PRIVATE_HOSTNAME`: Private hostname for internal access

## Examples

### Configuring for Local Development

```bash
update_networking.bat --http-port 8501 --public-domain localhost --public-port 8501 --public-protocol http
```

### Configuring for Production

```bash
update_networking.bat --http-port 8080 --public-domain gobeklitepe-5hzle.kinsta.app --public-port 443 --public-protocol https
```

### Adding IP Restrictions

```bash
update_networking.bat --add-ip-restriction 192.168.1.0/24
```

### Clearing IP Restrictions

```bash
update_networking.bat --clear-ip-restrictions
```

## Troubleshooting

If you encounter networking issues:

1. Run the network health check:
   ```bash
   check_network.bat
   ```

2. Check if the application is running:
   ```bash
   netstat -ano | findstr 8080
   ```

3. Verify that the WebSocket connection is working:
   ```bash
   python consolidated_websocket_test.py
   ```

4. Check the logs for any networking-related errors.

## Advanced Configuration

For advanced configuration options, edit the `networking.json` file directly or use the `update_networking.py` script with additional parameters.

See `update_networking.py --help` for all available options.
