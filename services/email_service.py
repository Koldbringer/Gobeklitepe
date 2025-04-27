"""
Email Service Module for HVAC CRM/ERP System

This module provides functionality for sending and receiving emails using Python's
standard libraries (smtplib, email.message, imaplib) as recommended.

Features:
- Send emails with text and HTML content
- Send emails with attachments
- Receive and process emails
- Email templates for common communications
- Email queue for handling failures and retries
"""

import os
import smtplib
import imaplib
import email
import logging
import time
import json
import re
import threading
import queue
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate, make_msgid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Load email configuration from environment variables
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "")
EMAIL_IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))

# Email templates directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "email"

# Email queue for handling retries
email_queue = queue.Queue()
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes


class EmailTemplate:
    """Class for managing email templates."""
    
    @staticmethod
    def load_template(template_name: str) -> str:
        """Load an email template from the templates directory."""
        template_path = TEMPLATE_DIR / f"{template_name}.html"
        if not template_path.exists():
            logger.warning(f"Template {template_name} not found at {template_path}")
            return ""
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    @staticmethod
    def render_template(template_name: str, context: Dict[str, Any]) -> str:
        """Render an email template with the given context."""
        template = EmailTemplate.load_template(template_name)
        if not template:
            return ""
        
        # Simple template rendering with string replacement
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return template


class EmailSender:
    """Class for sending emails."""
    
    @staticmethod
    def create_message(
        subject: str,
        from_email: str,
        to_emails: Union[str, List[str]],
        text_content: str = "",
        html_content: str = "",
        cc_emails: Union[str, List[str]] = None,
        bcc_emails: Union[str, List[str]] = None,
        attachments: List[Dict[str, Any]] = None,
        reply_to: str = None
    ) -> EmailMessage:
        """Create an email message."""
        msg = EmailMessage()
        
        # Set basic headers
        msg["Subject"] = subject
        msg["From"] = from_email
        
        # Handle different types of recipient lists
        if isinstance(to_emails, str):
            msg["To"] = to_emails
        else:
            msg["To"] = ", ".join(to_emails)
        
        if cc_emails:
            if isinstance(cc_emails, str):
                msg["Cc"] = cc_emails
            else:
                msg["Cc"] = ", ".join(cc_emails)
        
        if bcc_emails:
            if isinstance(bcc_emails, str):
                msg["Bcc"] = bcc_emails
            else:
                msg["Bcc"] = ", ".join(bcc_emails)
        
        if reply_to:
            msg["Reply-To"] = reply_to
        
        # Set date and message ID
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="hvacsolutions.com")
        
        # Set content
        if html_content:
            msg.add_alternative(html_content, subtype="html")
            if text_content:
                msg.add_alternative(text_content, subtype="plain")
        elif text_content:
            msg.set_content(text_content)
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                filename = attachment.get("filename", "")
                content = attachment.get("content", b"")
                content_type = attachment.get("content_type", "application/octet-stream")
                
                maintype, subtype = content_type.split("/", 1)
                msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
        
        return msg
    
    @staticmethod
    def send_email(
        subject: str,
        to_emails: Union[str, List[str]],
        text_content: str = "",
        html_content: str = "",
        from_email: str = None,
        cc_emails: Union[str, List[str]] = None,
        bcc_emails: Union[str, List[str]] = None,
        attachments: List[Dict[str, Any]] = None,
        reply_to: str = None,
        priority: int = 1  # 1 = high, 3 = normal, 5 = low
    ) -> bool:
        """Send an email."""
        if not from_email:
            from_email = EMAIL_HOST_USER
        
        try:
            # Create the email message
            msg = EmailSender.create_message(
                subject=subject,
                from_email=from_email,
                to_emails=to_emails,
                text_content=text_content,
                html_content=html_content,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
                attachments=attachments,
                reply_to=reply_to
            )
            
            # Connect to the SMTP server
            if EMAIL_USE_SSL:
                smtp = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
            else:
                smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                if EMAIL_USE_TLS:
                    smtp.starttls()
            
            # Login to the SMTP server
            smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            
            # Send the email
            recipients = []
            if isinstance(to_emails, str):
                recipients.append(to_emails)
            else:
                recipients.extend(to_emails)
            
            if cc_emails:
                if isinstance(cc_emails, str):
                    recipients.append(cc_emails)
                else:
                    recipients.extend(cc_emails)
            
            if bcc_emails:
                if isinstance(bcc_emails, str):
                    recipients.append(bcc_emails)
                else:
                    recipients.extend(bcc_emails)
            
            smtp.send_message(msg)
            smtp.quit()
            
            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            
            # Add to retry queue
            email_data = {
                "subject": subject,
                "to_emails": to_emails,
                "text_content": text_content,
                "html_content": html_content,
                "from_email": from_email,
                "cc_emails": cc_emails,
                "bcc_emails": bcc_emails,
                "attachments": attachments,
                "reply_to": reply_to,
                "priority": priority,
                "retries": 0,
                "next_retry": datetime.now() + timedelta(seconds=RETRY_DELAY)
            }
            email_queue.put(email_data)
            
            return False
    
    @staticmethod
    def send_template_email(
        template_name: str,
        context: Dict[str, Any],
        subject: str,
        to_emails: Union[str, List[str]],
        from_email: str = None,
        cc_emails: Union[str, List[str]] = None,
        bcc_emails: Union[str, List[str]] = None,
        attachments: List[Dict[str, Any]] = None,
        reply_to: str = None,
        priority: int = 3
    ) -> bool:
        """Send an email using a template."""
        html_content = EmailTemplate.render_template(template_name, context)
        
        # Generate plain text from HTML (simple version)
        text_content = re.sub(r'<.*?>', '', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return EmailSender.send_email(
            subject=subject,
            to_emails=to_emails,
            text_content=text_content,
            html_content=html_content,
            from_email=from_email,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            attachments=attachments,
            reply_to=reply_to,
            priority=priority
        )


class EmailReceiver:
    """Class for receiving emails."""
    
    @staticmethod
    def connect_to_imap() -> imaplib.IMAP4_SSL:
        """Connect to the IMAP server."""
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER, EMAIL_IMAP_PORT)
        mail.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        return mail
    
    @staticmethod
    def get_emails(
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = True,
        since_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get emails from the specified folder."""
        try:
            mail = EmailReceiver.connect_to_imap()
            mail.select(folder)
            
            search_criteria = []
            if unread_only:
                search_criteria.append("UNSEEN")
            
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                search_criteria.append(f'SINCE "{date_str}"')
            
            search_query = " ".join(search_criteria) if search_criteria else "ALL"
            status, data = mail.search(None, search_query)
            
            if status != "OK":
                logger.error(f"Failed to search emails: {status}")
                return []
            
            email_ids = data[0].split()
            if limit > 0:
                email_ids = email_ids[-limit:]
            
            emails = []
            for email_id in email_ids:
                status, data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    logger.error(f"Failed to fetch email {email_id}: {status}")
                    continue
                
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Parse email
                parsed_email = EmailReceiver.parse_email(email_message)
                parsed_email["id"] = email_id.decode("utf-8")
                emails.append(parsed_email)
            
            mail.close()
            mail.logout()
            
            return emails
        
        except Exception as e:
            logger.error(f"Error getting emails: {str(e)}")
            return []
    
    @staticmethod
    def parse_email(email_message: email.message.Message) -> Dict[str, Any]:
        """Parse an email message."""
        parsed_email = {
            "subject": email_message.get("Subject", ""),
            "from": email_message.get("From", ""),
            "to": email_message.get("To", ""),
            "date": email_message.get("Date", ""),
            "body_text": "",
            "body_html": "",
            "attachments": []
        }
        
        # Process email body and attachments
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip multipart containers
                if content_type == "multipart/alternative" or content_type == "multipart/mixed":
                    continue
                
                # Handle attachments
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment = {
                            "filename": filename,
                            "content": part.get_payload(decode=True),
                            "content_type": content_type
                        }
                        parsed_email["attachments"].append(attachment)
                else:
                    # Handle email body
                    if content_type == "text/plain":
                        parsed_email["body_text"] = part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        parsed_email["body_html"] = part.get_payload(decode=True).decode()
        else:
            # Handle non-multipart emails
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                parsed_email["body_text"] = email_message.get_payload(decode=True).decode()
            elif content_type == "text/html":
                parsed_email["body_html"] = email_message.get_payload(decode=True).decode()
        
        return parsed_email
    
    @staticmethod
    def mark_as_read(email_id: str, folder: str = "INBOX") -> bool:
        """Mark an email as read."""
        try:
            mail = EmailReceiver.connect_to_imap()
            mail.select(folder)
            
            mail.store(email_id.encode(), "+FLAGS", "\\Seen")
            
            mail.close()
            mail.logout()
            
            logger.info(f"Email {email_id} marked as read")
            return True
        
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    @staticmethod
    def move_email(email_id: str, destination_folder: str, source_folder: str = "INBOX") -> bool:
        """Move an email to another folder."""
        try:
            mail = EmailReceiver.connect_to_imap()
            mail.select(source_folder)
            
            # Copy the email to the destination folder
            result, data = mail.copy(email_id.encode(), destination_folder)
            if result == "OK":
                # Mark the original email for deletion
                mail.store(email_id.encode(), "+FLAGS", "\\Deleted")
                mail.expunge()
                
                logger.info(f"Email {email_id} moved to {destination_folder}")
                return True
            else:
                logger.error(f"Failed to copy email {email_id} to {destination_folder}: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Error moving email: {str(e)}")
            return False
        
        finally:
            mail.close()
            mail.logout()


def process_email_queue():
    """Process the email queue for retries."""
    while True:
        try:
            # Check if there are any emails in the queue
            if email_queue.empty():
                time.sleep(60)  # Sleep for 1 minute if queue is empty
                continue
            
            # Get the next email from the queue
            email_data = email_queue.get()
            
            # Check if it's time to retry
            if email_data["next_retry"] > datetime.now():
                # Put it back in the queue and sleep
                email_queue.put(email_data)
                time.sleep(10)
                continue
            
            # Retry sending the email
            logger.info(f"Retrying email to {email_data['to_emails']}, attempt {email_data['retries'] + 1}")
            
            try:
                # Create the email message
                msg = EmailSender.create_message(
                    subject=email_data["subject"],
                    from_email=email_data["from_email"] or EMAIL_HOST_USER,
                    to_emails=email_data["to_emails"],
                    text_content=email_data["text_content"],
                    html_content=email_data["html_content"],
                    cc_emails=email_data["cc_emails"],
                    bcc_emails=email_data["bcc_emails"],
                    attachments=email_data["attachments"],
                    reply_to=email_data["reply_to"]
                )
                
                # Connect to the SMTP server
                if EMAIL_USE_SSL:
                    smtp = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
                else:
                    smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                    if EMAIL_USE_TLS:
                        smtp.starttls()
                
                # Login to the SMTP server
                smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
                
                # Send the email
                recipients = []
                if isinstance(email_data["to_emails"], str):
                    recipients.append(email_data["to_emails"])
                else:
                    recipients.extend(email_data["to_emails"])
                
                if email_data["cc_emails"]:
                    if isinstance(email_data["cc_emails"], str):
                        recipients.append(email_data["cc_emails"])
                    else:
                        recipients.extend(email_data["cc_emails"])
                
                if email_data["bcc_emails"]:
                    if isinstance(email_data["bcc_emails"], str):
                        recipients.append(email_data["bcc_emails"])
                    else:
                        recipients.extend(email_data["bcc_emails"])
                
                smtp.send_message(msg)
                smtp.quit()
                
                logger.info(f"Email retry successful to {', '.join(recipients)}")
            
            except Exception as e:
                logger.error(f"Email retry failed: {str(e)}")
                
                # Increment retry count
                email_data["retries"] += 1
                
                # If we haven't reached the maximum number of retries, put it back in the queue
                if email_data["retries"] < MAX_RETRIES:
                    # Exponential backoff for retries
                    delay = RETRY_DELAY * (2 ** email_data["retries"])
                    email_data["next_retry"] = datetime.now() + timedelta(seconds=delay)
                    email_queue.put(email_data)
                else:
                    logger.error(f"Maximum retries reached for email to {email_data['to_emails']}")
        
        except Exception as e:
            logger.error(f"Error in email queue processor: {str(e)}")
            time.sleep(60)  # Sleep for 1 minute on error


# Start the email queue processor in a background thread
def start_email_queue_processor():
    """Start the email queue processor in a background thread."""
    thread = threading.Thread(target=process_email_queue, daemon=True)
    thread.start()
    logger.info("Email queue processor started")


# Common email functions for the application
def send_welcome_email(client_name: str, client_email: str) -> bool:
    """Send a welcome email to a new client."""
    context = {
        "client_name": client_name,
        "current_year": datetime.now().year
    }
    
    return EmailSender.send_template_email(
        template_name="welcome",
        context=context,
        subject="Witamy w HVAC Solutions!",
        to_emails=client_email
    )


def send_service_confirmation(
    client_name: str,
    client_email: str,
    service_date: str,
    service_type: str,
    technician_name: str
) -> bool:
    """Send a service confirmation email."""
    context = {
        "client_name": client_name,
        "service_date": service_date,
        "service_type": service_type,
        "technician_name": technician_name,
        "current_year": datetime.now().year
    }
    
    return EmailSender.send_template_email(
        template_name="service_confirmation",
        context=context,
        subject=f"Potwierdzenie wizyty serwisowej - {service_date}",
        to_emails=client_email
    )


def send_invoice(
    client_name: str,
    client_email: str,
    invoice_number: str,
    invoice_date: str,
    invoice_amount: float,
    invoice_pdf: bytes
) -> bool:
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
    
    return EmailSender.send_template_email(
        template_name="invoice",
        context=context,
        subject=f"Faktura nr {invoice_number}",
        to_emails=client_email,
        attachments=attachments
    )


def send_offer(
    client_name: str,
    client_email: str,
    offer_number: str,
    offer_date: str,
    offer_expiry_date: str,
    offer_pdf: bytes
) -> bool:
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
    
    return EmailSender.send_template_email(
        template_name="offer",
        context=context,
        subject=f"Oferta nr {offer_number}",
        to_emails=client_email,
        attachments=attachments
    )


def process_incoming_emails(limit: int = 10) -> List[Dict[str, Any]]:
    """Process incoming emails and return parsed data."""
    emails = EmailReceiver.get_emails(limit=limit, unread_only=True)
    processed_emails = []
    
    for email_data in emails:
        # Mark as read
        EmailReceiver.mark_as_read(email_data["id"])
        
        # Process the email (e.g., categorize, extract information)
        processed_email = {
            "id": email_data["id"],
            "subject": email_data["subject"],
            "from": email_data["from"],
            "date": email_data["date"],
            "body": email_data["body_text"] or email_data["body_html"],
            "has_attachments": len(email_data["attachments"]) > 0,
            "processed_date": datetime.now().isoformat()
        }
        
        processed_emails.append(processed_email)
    
    return processed_emails


# Initialize the module
def init():
    """Initialize the email service module."""
    # Create templates directory if it doesn't exist
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    
    # Start the email queue processor
    start_email_queue_processor()
    
    # Check if email configuration is valid
    if not EMAIL_HOST or not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        logger.warning("Email configuration is incomplete. Email functionality will be limited.")
    
    logger.info("Email service initialized")


# Initialize the module when imported
init()
