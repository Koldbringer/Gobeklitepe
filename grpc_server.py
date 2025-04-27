#!/usr/bin/env python
"""
gRPC Server for HVAC CRM/ERP System

This module implements a gRPC server for the HVAC CRM/ERP system.
"""

import os
import sys
import time
import logging
import grpc
import json
from concurrent import futures
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

# Import email service
try:
    from services.email_service import EmailSender, EmailReceiver
except ImportError:
    logger.warning("Email service not found. Email functionality will be limited.")
    EmailSender = None
    EmailReceiver = None

class HvacServiceServicer(service_pb2_grpc.HvacServiceServicer):
    """Implementation of the HvacService service."""
    
    def __init__(self):
        """Initialize the servicer."""
        self.start_time = datetime.now()
        self.version = "1.0.0"
        self.features = ["email", "grpc", "websocket"]
    
    def GetStatus(self, request, context):
        """Get system status."""
        logger.info(f"GetStatus request from client {request.client_id}")
        
        response = service_pb2.StatusResponse(
            status="running",
            version=self.version,
            timestamp=datetime.now().isoformat(),
            features=self.features
        )
        
        return response
    
    def SendEmail(self, request, context):
        """Send an email."""
        logger.info(f"SendEmail request to {request.to_email}")
        
        if EmailSender is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Email service not available")
            return service_pb2.EmailResponse()
        
        # Convert attachments
        attachments = []
        for attachment in request.attachments:
            attachments.append({
                "filename": attachment.filename,
                "content": attachment.content,
                "content_type": attachment.content_type
            })
        
        # Send email
        success = EmailSender.send_email(
            subject=request.subject,
            to_emails=request.to_email,
            text_content=request.text_content,
            html_content=request.html_content,
            from_email=request.from_email if request.from_email else None,
            cc_emails=list(request.cc_emails) if request.cc_emails else None,
            bcc_emails=list(request.bcc_emails) if request.bcc_emails else None,
            attachments=attachments if attachments else None,
            reply_to=request.reply_to if request.reply_to else None,
            priority=request.priority
        )
        
        if success:
            return service_pb2.EmailResponse(
                success=True,
                message="Email sent successfully",
                email_id=f"email-{int(time.time())}"
            )
        else:
            return service_pb2.EmailResponse(
                success=False,
                message="Failed to send email",
                email_id=""
            )
    
    def GetEmails(self, request, context):
        """Get emails."""
        logger.info(f"GetEmails request for folder {request.folder}")
        
        if EmailReceiver is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Email service not available")
            return service_pb2.EmailsResponse()
        
        # Parse since_date if provided
        since_date = None
        if request.since_date:
            try:
                since_date = datetime.fromisoformat(request.since_date)
            except ValueError:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Invalid since_date format: {request.since_date}")
                return service_pb2.EmailsResponse()
        
        # Get emails
        emails = EmailReceiver.get_emails(
            folder=request.folder,
            limit=request.limit,
            unread_only=request.unread_only,
            since_date=since_date
        )
        
        # Convert emails to response format
        response_emails = []
        for email_data in emails:
            attachments = []
            for attachment in email_data.get("attachments", []):
                attachments.append(service_pb2.Attachment(
                    filename=attachment.get("filename", ""),
                    content=attachment.get("content", b""),
                    content_type=attachment.get("content_type", "")
                ))
            
            response_emails.append(service_pb2.Email(
                id=email_data.get("id", ""),
                subject=email_data.get("subject", ""),
                from_=email_data.get("from", ""),
                to=email_data.get("to", ""),
                date=email_data.get("date", ""),
                body_text=email_data.get("body_text", ""),
                body_html=email_data.get("body_html", ""),
                attachments=attachments
            ))
        
        return service_pb2.EmailsResponse(
            emails=response_emails,
            total_count=len(response_emails),
            message=f"Retrieved {len(response_emails)} emails"
        )
    
    def HealthCheck(self, request, context):
        """Health check."""
        logger.info(f"HealthCheck request for service {request.service}")
        
        # Check if the requested service is available
        if request.service == "email":
            if EmailSender is not None and EmailReceiver is not None:
                status = service_pb2.HealthCheckResponse.ServingStatus.SERVING
            else:
                status = service_pb2.HealthCheckResponse.ServingStatus.NOT_SERVING
        elif request.service == "grpc":
            status = service_pb2.HealthCheckResponse.ServingStatus.SERVING
        else:
            status = service_pb2.HealthCheckResponse.ServingStatus.SERVICE_UNKNOWN
        
        return service_pb2.HealthCheckResponse(status=status)

def serve():
    """Start the gRPC server."""
    # Load configuration
    config = load_config()
    
    # Check if gRPC is enabled
    if not config.get("grpc_enabled", True):
        logger.error("gRPC is disabled in the configuration.")
        sys.exit(1)
    
    # Get gRPC configuration
    grpc_address = config.get("grpc_address", "0.0.0.0")
    grpc_port = config.get("grpc_port", 8080)
    grpc_max_workers = config.get("grpc_max_workers", 10)
    grpc_reflection_enabled = config.get("grpc_reflection_enabled", True)
    
    # Create gRPC server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=grpc_max_workers)
    )
    
    # Add servicer to server
    service_pb2_grpc.add_HvacServiceServicer_to_server(
        HvacServiceServicer(), server
    )
    
    # Enable reflection if requested
    if grpc_reflection_enabled:
        try:
            from grpc_reflection.v1alpha import reflection
            service_names = [
                service_pb2.DESCRIPTOR.services_by_name['HvacService'].full_name,
                reflection.SERVICE_NAME
            ]
            reflection.enable_server_reflection(service_names, server)
            logger.info("gRPC reflection enabled")
        except ImportError:
            logger.warning("grpcio-reflection not installed. Reflection disabled.")
    
    # Add secure port
    server_address = f"{grpc_address}:{grpc_port}"
    server.add_insecure_port(server_address)
    
    # Start server
    server.start()
    logger.info(f"gRPC server started on {server_address}")
    
    # Print URL
    grpc_url = get_grpc_url(config)
    logger.info(f"gRPC URL: {grpc_url}")
    
    try:
        # Keep server running
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        server.stop(0)

if __name__ == "__main__":
    serve()
