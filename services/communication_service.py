"""
Communication Service Module for HVAC CRM/ERP System

This module provides functionality for managing all types of communication with clients,
including emails, SMS, and phone call transcriptions. It integrates with the email_service
module for email functionality.

Features:
- Process and categorize incoming communications
- Store communications in the database
- Generate automated responses
- Schedule follow-up communications
- Analyze communication sentiment and content
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple

from services import email_service
from utils import db

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration from environment variables
ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "True").lower() == "true"
ENABLE_SMS = os.getenv("ENABLE_SMS", "False").lower() == "true"
ENABLE_LLM = os.getenv("ENABLE_LLM", "True").lower() == "true"


class CommunicationManager:
    """Class for managing all types of communication."""
    
    @staticmethod
    def save_communication(
        client_id: int,
        comm_type: str,
        direction: str,
        content: str,
        category: str = None,
        attachments: List[Dict[str, Any]] = None,
        sentiment_score: float = None,
        classification: str = None,
        transcription: str = None
    ) -> int:
        """Save a communication record to the database."""
        try:
            # Convert attachments to JSON if provided
            attachments_json = json.dumps(attachments) if attachments else None
            
            # Create communication data dictionary
            communication_data = {
                "id_klienta": client_id,
                "typ": comm_type,  # email, telefon, SMS
                "kierunek": direction,  # przychodzący/wychodzący
                "data_czas": datetime.now(),
                "treść": content,
                "transkrypcja": transcription,
                "kategoria": category,
                "status": "nowy",
                "załączniki": attachments_json,
                "analiza_sentymentu": sentiment_score,
                "klasyfikacja": classification
            }
            
            # Save to database
            query = """
            INSERT INTO komunikacja 
            (id_klienta, typ, kierunek, data_czas, treść, transkrypcja, kategoria, status, załączniki, analiza_sentymentu, klasyfikacja)
            VALUES 
            (%(id_klienta)s, %(typ)s, %(kierunek)s, %(data_czas)s, %(treść)s, %(transkrypcja)s, %(kategoria)s, %(status)s, %(załączniki)s, %(analiza_sentymentu)s, %(klasyfikacja)s)
            RETURNING id
            """
            
            result = db.execute_query(query, communication_data)
            communication_id = result[0]['id'] if result else None
            
            logger.info(f"Communication saved with ID: {communication_id}")
            return communication_id
        
        except Exception as e:
            logger.error(f"Error saving communication: {str(e)}")
            return None
    
    @staticmethod
    def get_client_communications(
        client_id: int,
        comm_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get communications for a specific client."""
        try:
            query = """
            SELECT * FROM komunikacja
            WHERE id_klienta = %s
            """
            
            params = [client_id]
            
            if comm_type:
                query += " AND typ = %s"
                params.append(comm_type)
            
            query += " ORDER BY data_czas DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            result = db.execute_query(query, params)
            return result if result else []
        
        except Exception as e:
            logger.error(f"Error getting client communications: {str(e)}")
            return []
    
    @staticmethod
    def get_communication_by_id(communication_id: int) -> Dict[str, Any]:
        """Get a specific communication by ID."""
        try:
            query = "SELECT * FROM komunikacja WHERE id = %s"
            result = db.execute_query(query, [communication_id])
            return result[0] if result else None
        
        except Exception as e:
            logger.error(f"Error getting communication by ID: {str(e)}")
            return None
    
    @staticmethod
    def update_communication_status(communication_id: int, status: str) -> bool:
        """Update the status of a communication."""
        try:
            query = "UPDATE komunikacja SET status = %s WHERE id = %s"
            db.execute_query(query, [status, communication_id], fetch=False)
            logger.info(f"Communication {communication_id} status updated to {status}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating communication status: {str(e)}")
            return False
    
    @staticmethod
    def categorize_communication(communication_id: int, category: str) -> bool:
        """Categorize a communication."""
        try:
            query = "UPDATE komunikacja SET kategoria = %s WHERE id = %s"
            db.execute_query(query, [category, communication_id], fetch=False)
            logger.info(f"Communication {communication_id} categorized as {category}")
            return True
        
        except Exception as e:
            logger.error(f"Error categorizing communication: {str(e)}")
            return False
    
    @staticmethod
    def analyze_sentiment(communication_id: int, content: str) -> float:
        """Analyze the sentiment of a communication."""
        if not ENABLE_LLM:
            logger.warning("LLM is disabled. Skipping sentiment analysis.")
            return None
        
        try:
            # This is a placeholder for actual sentiment analysis
            # In a real implementation, you would use an LLM or sentiment analysis service
            # For now, we'll return a random score between -1 and 1
            import random
            sentiment_score = random.uniform(-1, 1)
            
            # Update the communication record
            query = "UPDATE komunikacja SET analiza_sentymentu = %s WHERE id = %s"
            db.execute_query(query, [sentiment_score, communication_id], fetch=False)
            
            logger.info(f"Communication {communication_id} sentiment analyzed: {sentiment_score}")
            return sentiment_score
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None
    
    @staticmethod
    def classify_communication(communication_id: int, content: str) -> str:
        """Classify a communication into categories."""
        if not ENABLE_LLM:
            logger.warning("LLM is disabled. Skipping classification.")
            return None
        
        try:
            # This is a placeholder for actual classification
            # In a real implementation, you would use an LLM or classification service
            # For now, we'll randomly select from predefined categories
            categories = ["zapytanie", "reklamacja", "podziękowanie", "zamówienie", "inne"]
            import random
            classification = random.choice(categories)
            
            # Update the communication record
            query = "UPDATE komunikacja SET klasyfikacja = %s WHERE id = %s"
            db.execute_query(query, [classification, communication_id], fetch=False)
            
            logger.info(f"Communication {communication_id} classified as {classification}")
            return classification
        
        except Exception as e:
            logger.error(f"Error classifying communication: {str(e)}")
            return None


class EmailManager:
    """Class for managing email communications."""
    
    @staticmethod
    def send_email(
        client_id: int,
        subject: str,
        content: str,
        to_email: str,
        attachments: List[Dict[str, Any]] = None,
        html_content: str = None
    ) -> int:
        """Send an email and save it as a communication."""
        if not ENABLE_EMAIL:
            logger.warning("Email functionality is disabled.")
            return None
        
        try:
            # Send the email
            email_sent = email_service.EmailSender.send_email(
                subject=subject,
                to_emails=to_email,
                text_content=content,
                html_content=html_content or "",
                attachments=attachments
            )
            
            if not email_sent:
                logger.error(f"Failed to send email to {to_email}")
                return None
            
            # Save the communication record
            communication_id = CommunicationManager.save_communication(
                client_id=client_id,
                comm_type="email",
                direction="wychodzący",
                content=content,
                category="wysłany",
                attachments=attachments
            )
            
            return communication_id
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return None
    
    @staticmethod
    def send_template_email(
        client_id: int,
        template_name: str,
        context: Dict[str, Any],
        subject: str,
        to_email: str,
        attachments: List[Dict[str, Any]] = None
    ) -> int:
        """Send an email using a template and save it as a communication."""
        if not ENABLE_EMAIL:
            logger.warning("Email functionality is disabled.")
            return None
        
        try:
            # Render the template
            html_content = email_service.EmailTemplate.render_template(template_name, context)
            
            if not html_content:
                logger.error(f"Failed to render email template {template_name}")
                return None
            
            # Generate plain text from HTML (simple version)
            import re
            text_content = re.sub(r'<.*?>', '', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Send the email
            return EmailManager.send_email(
                client_id=client_id,
                subject=subject,
                content=text_content,
                to_email=to_email,
                attachments=attachments,
                html_content=html_content
            )
        
        except Exception as e:
            logger.error(f"Error sending template email: {str(e)}")
            return None
    
    @staticmethod
    def process_incoming_emails(limit: int = 10) -> List[int]:
        """Process incoming emails and save them as communications."""
        if not ENABLE_EMAIL:
            logger.warning("Email functionality is disabled.")
            return []
        
        try:
            # Get incoming emails
            emails = email_service.process_incoming_emails(limit=limit)
            
            if not emails:
                logger.info("No new emails to process")
                return []
            
            communication_ids = []
            
            for email_data in emails:
                # Extract email information
                from_email = email_data["from"]
                subject = email_data["subject"]
                body = email_data["body"]
                
                # Find the client by email
                query = "SELECT id FROM klienci WHERE email = %s"
                result = db.execute_query(query, [from_email])
                
                if not result:
                    logger.warning(f"No client found with email {from_email}")
                    continue
                
                client_id = result[0]["id"]
                
                # Save the communication
                communication_id = CommunicationManager.save_communication(
                    client_id=client_id,
                    comm_type="email",
                    direction="przychodzący",
                    content=body,
                    category="odebrany"
                )
                
                if communication_id:
                    communication_ids.append(communication_id)
                    
                    # Analyze sentiment and classify
                    CommunicationManager.analyze_sentiment(communication_id, body)
                    CommunicationManager.classify_communication(communication_id, body)
            
            logger.info(f"Processed {len(communication_ids)} incoming emails")
            return communication_ids
        
        except Exception as e:
            logger.error(f"Error processing incoming emails: {str(e)}")
            return []


class SMSManager:
    """Class for managing SMS communications."""
    
    @staticmethod
    def send_sms(
        client_id: int,
        content: str,
        phone_number: str
    ) -> int:
        """Send an SMS and save it as a communication."""
        if not ENABLE_SMS:
            logger.warning("SMS functionality is disabled.")
            return None
        
        try:
            # This is a placeholder for actual SMS sending
            # In a real implementation, you would use a service like Twilio
            logger.info(f"Sending SMS to {phone_number}: {content}")
            
            # Save the communication record
            communication_id = CommunicationManager.save_communication(
                client_id=client_id,
                comm_type="SMS",
                direction="wychodzący",
                content=content,
                category="wysłany"
            )
            
            return communication_id
        
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return None


class PhoneCallManager:
    """Class for managing phone call communications."""
    
    @staticmethod
    def save_call_transcription(
        client_id: int,
        transcription: str,
        call_duration: int = None,
        call_date: datetime = None
    ) -> int:
        """Save a phone call transcription as a communication."""
        try:
            # Save the communication record
            communication_id = CommunicationManager.save_communication(
                client_id=client_id,
                comm_type="telefon",
                direction="przychodzący",  # This could be parameterized
                content=f"Rozmowa telefoniczna, czas trwania: {call_duration} sekund",
                category="transkrypcja",
                transcription=transcription
            )
            
            if communication_id:
                # Analyze sentiment and classify
                CommunicationManager.analyze_sentiment(communication_id, transcription)
                CommunicationManager.classify_communication(communication_id, transcription)
            
            return communication_id
        
        except Exception as e:
            logger.error(f"Error saving call transcription: {str(e)}")
            return None


# Common communication functions for the application
def send_welcome_email(client_id: int, client_name: str, client_email: str) -> int:
    """Send a welcome email to a new client."""
    context = {
        "client_name": client_name,
        "current_year": datetime.now().year
    }
    
    return EmailManager.send_template_email(
        client_id=client_id,
        template_name="welcome",
        context=context,
        subject="Witamy w HVAC Solutions!",
        to_email=client_email
    )


def send_service_confirmation(
    client_id: int,
    client_name: str,
    client_email: str,
    service_date: str,
    service_type: str,
    technician_name: str
) -> int:
    """Send a service confirmation email."""
    context = {
        "client_name": client_name,
        "service_date": service_date,
        "service_type": service_type,
        "technician_name": technician_name,
        "current_year": datetime.now().year
    }
    
    return EmailManager.send_template_email(
        client_id=client_id,
        template_name="service_confirmation",
        context=context,
        subject=f"Potwierdzenie wizyty serwisowej - {service_date}",
        to_email=client_email
    )


def send_invoice(
    client_id: int,
    client_name: str,
    client_email: str,
    invoice_number: str,
    invoice_date: str,
    invoice_amount: float,
    invoice_pdf: bytes
) -> int:
    """Send an invoice email with PDF attachment."""
    context = {
        "client_name": client_name,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "invoice_amount": invoice_amount,
        "current_year": datetime.now().year
    }
    
    attachments = [{
        "filename": f"Faktura_{invoice_number}.pdf",
        "content": invoice_pdf,
        "content_type": "application/pdf"
    }]
    
    return EmailManager.send_template_email(
        client_id=client_id,
        template_name="invoice",
        context=context,
        subject=f"Faktura nr {invoice_number}",
        to_email=client_email,
        attachments=attachments
    )


def send_offer(
    client_id: int,
    client_name: str,
    client_email: str,
    offer_number: str,
    offer_date: str,
    offer_expiry_date: str,
    offer_pdf: bytes
) -> int:
    """Send an offer email with PDF attachment."""
    context = {
        "client_name": client_name,
        "offer_number": offer_number,
        "offer_date": offer_date,
        "offer_expiry_date": offer_expiry_date,
        "current_year": datetime.now().year
    }
    
    attachments = [{
        "filename": f"Oferta_{offer_number}.pdf",
        "content": offer_pdf,
        "content_type": "application/pdf"
    }]
    
    return EmailManager.send_template_email(
        client_id=client_id,
        template_name="offer",
        context=context,
        subject=f"Oferta nr {offer_number}",
        to_email=client_email,
        attachments=attachments
    )


def process_incoming_communications():
    """Process all types of incoming communications."""
    # Process incoming emails
    email_ids = EmailManager.process_incoming_emails()
    
    # Here you could add processing for other communication types
    # such as SMS or voicemail transcriptions
    
    return {
        "emails": len(email_ids)
    }


# Initialize the module
def init():
    """Initialize the communication service module."""
    logger.info("Communication service initialized")


# Initialize the module when imported
init()
