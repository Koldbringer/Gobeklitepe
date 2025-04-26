import streamlit as st
import os
from config import APP_NAME, COMPANY_NAME, LOGO_PATH

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        # Logo and app name
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        else:
            st.title(APP_NAME)
        
        st.caption(COMPANY_NAME)
        
        # Separator
        st.markdown("---")
        
        # Navigation
        st.subheader("Nawigacja")
        
        # Dashboard
        if st.sidebar.button("📊 Panel główny", use_container_width=True):
            st.session_state.page = "dashboard"
        
        # Clients
        if st.sidebar.button("👥 Klienci", use_container_width=True):
            st.session_state.page = "clients"
        
        # Devices
        if st.sidebar.button("🔧 Urządzenia", use_container_width=True):
            st.session_state.page = "devices"
        
        # Buildings
        if st.sidebar.button("🏢 Budynki/Lokalizacje", use_container_width=True):
            st.session_state.page = "buildings"
        
        # Service orders
        if st.sidebar.button("📋 Zlecenia serwisowe", use_container_width=True):
            st.session_state.page = "service_orders"
        
        # Calendar
        if st.sidebar.button("📅 Kalendarz", use_container_width=True):
            st.session_state.page = "calendar"
        
        # Offers and invoices
        if st.sidebar.button("💰 Oferty i faktury", use_container_width=True):
            st.session_state.page = "offers_invoices"
        
        # Inventory
        if st.sidebar.button("📦 Magazyn części", use_container_width=True):
            st.session_state.page = "inventory"
        
        # Reports
        if st.sidebar.button("📈 Raporty", use_container_width=True):
            st.session_state.page = "reports"
        
        # Communication
        if st.sidebar.button("✉️ Komunikacja", use_container_width=True):
            st.session_state.page = "communication"
        
        # Visualizations
        if st.sidebar.button("🖼️ Wizualizacje/zdjęcia", use_container_width=True):
            st.session_state.page = "visualizations"
        
        # Automation
        if st.sidebar.button("⚙️ Automatyzacja/procesy", use_container_width=True):
            st.session_state.page = "automation"
        
        # Client portal
        if st.sidebar.button("🌐 Panel klienta", use_container_width=True):
            st.session_state.page = "client_portal"
        
        # Separator
        st.markdown("---")
        
        # User section
        st.subheader("Użytkownik")
        
        # User info (placeholder)
        st.text("Zalogowany jako: Admin")
        
        # Logout button
        if st.button("Wyloguj", use_container_width=True):
            # Placeholder for logout functionality
            st.session_state.clear()
        
        # Version info
        st.caption(f"Wersja: 1.0.0")

def initialize_session_state():
    """Initialize session state variables."""
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
