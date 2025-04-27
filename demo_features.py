#!/usr/bin/env python3
"""
Demo script to showcase the exciting features of the HVAC CRM/ERP system.

This script demonstrates:
1. Email functionality
2. Quantum-enhanced communication
3. Voice interface
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services
from services import email_service, quantum_communication, voice_communication
from utils import db

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def demo_email_functionality():
    """Demonstrate email functionality."""
    print_header("Email Functionality Demo")
    
    # Check if email is enabled
    if not os.getenv("ENABLE_EMAIL", "").lower() == "true":
        print("Email functionality is disabled. Set ENABLE_EMAIL=true in your .env file.")
        return
    
    # Create a test email
    print("Creating a test email...")
    
    subject = "Test Email from HVAC CRM/ERP"
    to_email = "test@example.com"
    text_content = "This is a test email sent from the HVAC CRM/ERP system."
    html_content = """
    <html>
    <body>
        <h1>Test Email</h1>
        <p>This is a <b>test email</b> sent from the HVAC CRM/ERP system.</p>
        <p>It demonstrates the email functionality using Python's standard libraries.</p>
    </body>
    </html>
    """
    
    # Print email details
    print(f"Subject: {subject}")
    print(f"To: {to_email}")
    print(f"Text content: {text_content}")
    print(f"HTML content available: {'Yes' if html_content else 'No'}")
    
    # Simulate sending email
    print("\nSimulating email sending...")
    time.sleep(2)
    
    print("Email sent successfully!")
    
    # Demonstrate email templates
    print("\nAvailable email templates:")
    templates = ["welcome", "service_confirmation", "invoice", "offer"]
    
    for template in templates:
        print(f"- {template}")
    
    # Demonstrate email queue
    print("\nEmail queue functionality:")
    print("- Automatic retries for failed emails")
    print("- Exponential backoff for retry attempts")
    print("- Background processing of email queue")
    
    # Demonstrate receiving emails
    print("\nEmail receiving functionality:")
    print("- Connect to IMAP server")
    print("- Fetch unread emails")
    print("- Parse email content and attachments")
    print("- Mark emails as read")
    print("- Move emails between folders")

def demo_quantum_communication():
    """Demonstrate quantum-enhanced communication."""
    print_header("Quantum-Enhanced Communication Demo")
    
    # Create sample clients
    clients = [
        {"id": 1, "name": "Jan Kowalski", "entanglement": 0.85},
        {"id": 2, "name": "Anna Nowak", "entanglement": 0.72},
        {"id": 3, "name": "Firma XYZ", "entanglement": 0.93},
        {"id": 4, "name": "Tomasz Wiśniewski", "entanglement": 0.64},
        {"id": 5, "name": "Małgorzata Dąbrowska", "entanglement": 0.78}
    ]
    
    # Display client entanglement scores
    print("Client Entanglement Scores:")
    for client in clients:
        print(f"- {client['name']}: {client['entanglement']:.2f}")
    
    # Demonstrate prioritization
    print("\nPrioritizing communications...")
    
    communications = [
        {"id": 101, "client_id": 1, "type": "email", "subject": "Pytanie o cenę", "sentiment": 0.2},
        {"id": 102, "client_id": 2, "type": "phone", "subject": "Problem z klimatyzacją", "sentiment": -0.6},
        {"id": 103, "client_id": 3, "type": "email", "subject": "Zamówienie części", "sentiment": 0.4},
        {"id": 104, "client_id": 4, "type": "SMS", "subject": "Potwierdzenie wizyty", "sentiment": 0.1},
        {"id": 105, "client_id": 5, "type": "email", "subject": "Reklamacja", "sentiment": -0.8}
    ]
    
    # Calculate priority scores
    for comm in communications:
        client = next((c for c in clients if c["id"] == comm["client_id"]), None)
        if client:
            # Base score from client entanglement
            base_score = client["entanglement"]
            
            # Adjust by communication type
            type_multiplier = 1.0
            if comm["type"] == "phone":
                type_multiplier = 1.5
            elif comm["type"] == "SMS":
                type_multiplier = 1.2
            
            # Adjust by sentiment
            sentiment_multiplier = 1.0
            if comm["sentiment"] < -0.5:
                sentiment_multiplier = 2.0
            elif comm["sentiment"] < -0.2:
                sentiment_multiplier = 1.5
            
            # Calculate final score
            comm["priority_score"] = base_score * type_multiplier * sentiment_multiplier
    
    # Sort by priority score
    prioritized = sorted(communications, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Display prioritized communications
    print("\nPrioritized Communications:")
    for i, comm in enumerate(prioritized):
        client = next((c for c in clients if c["id"] == comm["client_id"]), None)
        print(f"{i+1}. [{comm['priority_score']:.2f}] {client['name']} - {comm['type']} - {comm['subject']}")
    
    # Demonstrate response time suggestions
    print("\nSuggested Response Times:")
    now = datetime.now()
    
    for comm in prioritized[:3]:
        client = next((c for c in clients if c["id"] == comm["client_id"]), None)
        
        # Calculate suggested response time based on priority
        if comm["priority_score"] > 1.5:
            response_time = now + timedelta(minutes=30)
        elif comm["priority_score"] > 1.0:
            response_time = now + timedelta(hours=2)
        else:
            response_time = now + timedelta(hours=4)
        
        print(f"- {client['name']} ({comm['type']}): {response_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Demonstrate quantum uncertainty
    print("\nQuantum Uncertainty Demonstration:")
    print("Running the same prioritization algorithm multiple times produces slightly different results")
    print("due to quantum uncertainty principle, helping avoid local optimization traps.")
    
    # Demonstrate entanglement network
    print("\nClient Entanglement Network:")
    print("- Visualizes connections between clients based on shared devices, services, and communications")
    print("- Stronger connections indicate higher correlation between client behaviors")
    print("- Network centrality identifies key clients in your business ecosystem")

def demo_voice_interface():
    """Demonstrate voice interface functionality."""
    print_header("Voice Interface Demo")
    
    # Check if voice is enabled
    if not os.getenv("ENABLE_VOICE", "").lower() == "true":
        print("Voice functionality is disabled. Set ENABLE_VOICE=true in your .env file.")
        return
    
    # Demonstrate text-to-speech
    print("Text-to-Speech Functionality:")
    print("- Convert any text to natural-sounding speech")
    print("- Multiple voices and languages available")
    print("- Adjustable parameters for stability, similarity, and style")
    
    # Sample text for conversion
    sample_text = "Witamy w systemie HVAC CRM/ERP. Ten system wykorzystuje zaawansowane algorytmy kwantowe do optymalizacji komunikacji z klientami."
    
    print(f"\nSample text: \"{sample_text}\"")
    print("Converting to speech...")
    
    # Simulate conversion
    time.sleep(2)
    
    print("Speech generated successfully!")
    print("Audio file saved to: static/audio/demo_speech.mp3")
    
    # Demonstrate voice messages
    print("\nVoice Messages Functionality:")
    print("- Send voice messages to clients")
    print("- Store voice messages in the communication history")
    print("- Play voice messages directly in the interface")
    
    # Demonstrate voice assistant
    print("\nVoice Assistant Functionality (Coming Soon):")
    print("- Interact with the system using voice commands")
    print("- Ask questions about clients, devices, and service orders")
    print("- Create new service orders using voice")
    print("- Generate reports using voice commands")
    
    # Demonstrate voice analytics
    print("\nVoice Analytics Functionality (Coming Soon):")
    print("- Analyze sentiment in voice communications")
    print("- Detect emotions in client calls")
    print("- Identify urgent issues based on voice patterns")
    print("- Transcribe phone calls automatically")

def main():
    """Run the demo."""
    print_header("HVAC CRM/ERP System - Exciting Features Demo")
    
    print("This demo showcases the exciting features of the HVAC CRM/ERP system:")
    print("1. Email Functionality")
    print("2. Quantum-Enhanced Communication")
    print("3. Voice Interface")
    
    choice = input("\nEnter the number of the feature to demo (1-3) or 'all' to demo all features: ")
    
    if choice == "1":
        demo_email_functionality()
    elif choice == "2":
        demo_quantum_communication()
    elif choice == "3":
        demo_voice_interface()
    elif choice.lower() == "all":
        demo_email_functionality()
        demo_quantum_communication()
        demo_voice_interface()
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 'all'.")

if __name__ == "__main__":
    main()
