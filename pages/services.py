import streamlit as st
import os
import sys
import logging
from components.sidebar import initialize_session_state, render_sidebar
from components.services_status import render_services_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def render_services_page():
    """Render the services page."""
    st.title("Integrated Services")
    
    st.markdown("""
    This page provides an overview of the integrated services in the HVAC CRM/ERP system.
    You can check the status of each service and perform basic operations.
    """)
    
    # Display services status
    render_services_status()
    
    # Display documentation
    with st.expander("Services Documentation"):
        st.markdown("""
        ## n8n Workflow Automation
        
        n8n is a powerful workflow automation tool that can be used to automate various tasks in the HVAC CRM/ERP system.
        
        ### Example Use Cases:
        - Automatically create service orders based on sensor data
        - Send notifications when inventory levels are low
        - Generate reports and send them via email
        - Integrate with external APIs and services
        
        ## Mastra AI Agent Framework
        
        Mastra AI is an agent framework that can be used to create AI-powered assistants for the HVAC CRM/ERP system.
        
        ### Example Use Cases:
        - Create a customer service chatbot
        - Develop an AI assistant for technicians
        - Build an AI-powered recommendation system for parts and services
        - Automate document analysis and data extraction
        
        ## Maxun Web Data Extraction
        
        Maxun is a web data extraction tool that can be used to gather data from various sources for the HVAC CRM/ERP system.
        
        ### Example Use Cases:
        - Extract product information from manufacturer websites
        - Gather pricing data from competitors
        - Collect weather data for predictive maintenance
        - Extract information from PDF documents and forms
        
        ## MinIO Object Storage
        
        MinIO is an object storage system used to store documents, images, and other files in the HVAC CRM/ERP system.
        
        ### Example Use Cases:
        - Store customer documents and contracts
        - Save equipment manuals and documentation
        - Archive service reports and photos
        - Store backup files and exports
        """)
    
    # Display integration examples
    with st.expander("Integration Examples"):
        st.markdown("""
        ## Example 1: Automated Document Processing
        
        1. Use Maxun to extract data from scanned invoices
        2. Store the original documents in MinIO
        3. Use n8n to process the extracted data and update the database
        4. Use Mastra AI to validate and categorize the documents
        
        ## Example 2: Predictive Maintenance
        
        1. Use n8n to collect sensor data from HVAC equipment
        2. Store the data in the PostgreSQL database
        3. Use Mastra AI to analyze the data and predict maintenance needs
        4. Generate service orders automatically when maintenance is needed
        
        ## Example 3: Customer Portal
        
        1. Use the HVAC CRM/ERP system to manage customer information
        2. Use MinIO to store customer documents
        3. Use n8n to send notifications to customers
        4. Use Mastra AI to provide personalized recommendations
        """)

def main():
    """Main function to render the services page."""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render services page
    render_services_page()

if __name__ == "__main__":
    main()
