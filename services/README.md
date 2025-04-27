# Email and Communication Services

This directory contains services for handling email and other communication in the HVAC CRM/ERP system.

## Email Service

The `email_service.py` module provides functionality for sending and receiving emails using Python's standard libraries (smtplib, email.message, imaplib) as recommended. It offers:

- Sending emails with text and HTML content
- Sending emails with attachments
- Receiving and processing emails
- Email templates for common communications
- Email queue for handling failures and retries

### Usage Examples

#### Sending a Simple Email

```python
from services import email_service

# Send a simple email
email_service.EmailSender.send_email(
    subject="Test Email",
    to_emails="recipient@example.com",
    text_content="This is a test email sent from Python.",
    from_email="sender@example.com"  # Optional, defaults to EMAIL_HOST_USER
)
```

#### Sending an Email with Template

```python
from services import email_service

# Define context for template
context = {
    "client_name": "John Doe",
    "current_year": 2025
}

# Send email using template
email_service.EmailSender.send_template_email(
    template_name="welcome",
    context=context,
    subject="Welcome to HVAC Solutions!",
    to_emails="john.doe@example.com"
)
```

#### Receiving Emails

```python
from services import email_service

# Get recent unread emails
emails = email_service.EmailReceiver.get_emails(
    folder="INBOX",
    limit=10,
    unread_only=True
)

# Process emails
for email_data in emails:
    print(f"From: {email_data['from']}")
    print(f"Subject: {email_data['subject']}")
    print(f"Body: {email_data['body_text']}")
    
    # Mark as read
    email_service.EmailReceiver.mark_as_read(email_data["id"])
```

## Communication Service

The `communication_service.py` module provides a higher-level interface for managing all types of communication with clients, including emails, SMS, and phone call transcriptions. It integrates with the `email_service` module for email functionality.

### Usage Examples

#### Sending a Welcome Email to a Client

```python
from services import communication_service

# Send welcome email
communication_service.send_welcome_email(
    client_id=123,
    client_name="John Doe",
    client_email="john.doe@example.com"
)
```

#### Sending a Service Confirmation

```python
from services import communication_service

# Send service confirmation
communication_service.send_service_confirmation(
    client_id=123,
    client_name="John Doe",
    client_email="john.doe@example.com",
    service_date="2025-05-01 14:30",
    service_type="Maintenance",
    technician_name="Mike Smith"
)
```

#### Processing Incoming Communications

```python
from services import communication_service

# Process all incoming communications
result = communication_service.process_incoming_communications()
print(f"Processed {result['emails']} new emails")
```

## Configuration

Both services use environment variables for configuration. Make sure to set the following variables in your `.env` file:

```
# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_IMAP_SERVER=imap.example.com
EMAIL_IMAP_PORT=993

# Feature Flags
ENABLE_EMAIL=true
ENABLE_SMS=false
ENABLE_LLM=true
```

## Email Templates

Email templates are stored in the `templates/email/` directory as HTML files. The following templates are available:

- `welcome.html`: Welcome email for new clients
- `service_confirmation.html`: Confirmation of a service appointment
- `invoice.html`: Invoice email with PDF attachment
- `offer.html`: Offer email with PDF attachment

You can create new templates by adding HTML files to the templates directory and using the `EmailTemplate.render_template()` method to render them with context variables.
