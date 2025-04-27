#!/usr/bin/env python
"""
gRPC Client for HVAC CRM/ERP System

This module implements a gRPC client for the HVAC CRM/ERP system.
"""

import os
import sys
import logging
import grpc
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import networking configuration
from networking_config import load_config, get_grpc_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Check if generated code exists
try:
    from generated import service_pb2, service_pb2_grpc
except ImportError:
    logger.error("Generated gRPC code not found. Please run generate_grpc.py first.")
    sys.exit(1)

def get_status(stub, client_id: str = "test-client"):
    """Get system status."""
    logger.info(f"Getting status for client {client_id}")
    
    request = service_pb2.StatusRequest(client_id=client_id)
    response = stub.GetStatus(request)
    
    logger.info(f"Status: {response.status}")
    logger.info(f"Version: {response.version}")
    logger.info(f"Timestamp: {response.timestamp}")
    logger.info(f"Features: {', '.join(response.features)}")
    
    return response

def send_email(stub, subject: str, to_email: str, text_content: str, html_content: str = ""):
    """Send an email."""
    logger.info(f"Sending email to {to_email}")
    
    request = service_pb2.EmailRequest(
        subject=subject,
        to_email=to_email,
        text_content=text_content,
        html_content=html_content
    )
    
    response = stub.SendEmail(request)
    
    if response.success:
        logger.info(f"Email sent successfully: {response.email_id}")
    else:
        logger.error(f"Failed to send email: {response.message}")
    
    return response

def get_emails(stub, folder: str = "INBOX", limit: int = 10, unread_only: bool = True):
    """Get emails."""
    logger.info(f"Getting emails from {folder}")
    
    request = service_pb2.EmailsRequest(
        folder=folder,
        limit=limit,
        unread_only=unread_only
    )
    
    response = stub.GetEmails(request)
    
    logger.info(f"Retrieved {response.total_count} emails")
    for i, email in enumerate(response.emails):
        logger.info(f"Email {i+1}:")
        logger.info(f"  Subject: {email.subject}")
        logger.info(f"  From: {email.from_}")
        logger.info(f"  Date: {email.date}")
    
    return response

def health_check(stub, service: str = "grpc"):
    """Health check."""
    logger.info(f"Checking health of service {service}")
    
    request = service_pb2.HealthCheckRequest(service=service)
    response = stub.HealthCheck(request)
    
    status_map = {
        service_pb2.HealthCheckResponse.ServingStatus.UNKNOWN: "UNKNOWN",
        service_pb2.HealthCheckResponse.ServingStatus.SERVING: "SERVING",
        service_pb2.HealthCheckResponse.ServingStatus.NOT_SERVING: "NOT_SERVING",
        service_pb2.HealthCheckResponse.ServingStatus.SERVICE_UNKNOWN: "SERVICE_UNKNOWN"
    }
    
    status = status_map.get(response.status, "UNKNOWN")
    logger.info(f"Health status: {status}")
    
    return response

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="gRPC client for HVAC CRM/ERP system")
    parser.add_argument("--action", choices=["status", "email", "emails", "health"], default="status",
                        help="Action to perform")
    parser.add_argument("--client-id", default="test-client",
                        help="Client ID for status request")
    parser.add_argument("--subject", default="Test Email",
                        help="Subject for email request")
    parser.add_argument("--to-email", default="test@example.com",
                        help="Recipient for email request")
    parser.add_argument("--text-content", default="This is a test email",
                        help="Text content for email request")
    parser.add_argument("--folder", default="INBOX",
                        help="Folder for emails request")
    parser.add_argument("--limit", type=int, default=10,
                        help="Limit for emails request")
    parser.add_argument("--unread-only", type=bool, default=True,
                        help="Unread only for emails request")
    parser.add_argument("--service", default="grpc",
                        help="Service for health check request")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Get gRPC URL
    grpc_url = get_grpc_url(config)
    logger.info(f"Connecting to gRPC server at {grpc_url}")
    
    # Parse gRPC URL
    grpc_address = config.get("grpc_address", "0.0.0.0")
    grpc_port = config.get("grpc_port", 8080)
    server_address = f"{grpc_address}:{grpc_port}"
    
    # Create gRPC channel
    channel = grpc.insecure_channel(server_address)
    
    # Create stub
    stub = service_pb2_grpc.HvacServiceStub(channel)
    
    try:
        # Perform action
        if args.action == "status":
            get_status(stub, args.client_id)
        elif args.action == "email":
            send_email(stub, args.subject, args.to_email, args.text_content)
        elif args.action == "emails":
            get_emails(stub, args.folder, args.limit, args.unread_only)
        elif args.action == "health":
            health_check(stub, args.service)
        else:
            logger.error(f"Unknown action: {args.action}")
            sys.exit(1)
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()}: {e.details()}")
        sys.exit(1)
    finally:
        # Close channel
        channel.close()

if __name__ == "__main__":
    main()
