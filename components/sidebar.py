import streamlit as st
import os
import logging
from datetime import datetime
from config import APP_NAME, COMPANY_NAME, LOGO_PATH, PRIMARY_COLOR

logger = logging.getLogger(__name__)

# Define navigation structure
NAVIGATION = [
    {
        "section": "Główne",
        "items": [
            {"icon": "📊", "name": "Panel główny", "page": "dashboard"},
            {"icon": "👥", "name": "Klienci", "page": "clients"},
            {"icon": "🔧", "name": "Urządzenia", "page": "devices"},
            {"icon": "🏢", "name": "Budynki/Lokalizacje", "page": "buildings"},
        ]
    },
    {
        "section": "Operacje",
        "items": [
            {"icon": "📋", "name": "Zlecenia serwisowe", "page": "service_orders"},
            {"icon": "📅", "name": "Kalendarz", "page": "calendar"},
            {"icon": "💰", "name": "Oferty i faktury", "page": "offers_invoices"},
            {"icon": "📦", "name": "Magazyn części", "page": "inventory"},
        ]
    },
    {
        "section": "Analiza i komunikacja",
        "items": [
            {"icon": "📈", "name": "Raporty", "page": "reports"},
            {"icon": "✉️", "name": "Komunikacja", "page": "communication"},
            {"icon": "🎙️", "name": "Interfejs głosowy", "page": "voice_interface"},
            {"icon": "🖼️", "name": "Wizualizacje/zdjęcia", "page": "visualizations"},
        ]
    },
    {
        "section": "Zaawansowane",
        "items": [
            {"icon": "🔬", "name": "Kwantowy Dashboard", "page": "quantum_dashboard"},
            {"icon": "⚙️", "name": "Automatyzacja/procesy", "page": "automation"},
            {"icon": "🌐", "name": "Panel klienta", "page": "client_portal"},
        ]
    }
]

def render_sidebar():
    """Render the sidebar navigation."""
    try:
        with st.sidebar:
            # Logo and app name
            col1, col2 = st.columns([1, 3])
            with col1:
                if os.path.exists(LOGO_PATH):
                    st.image(LOGO_PATH, width=60)
            with col2:
                st.markdown(f"<h2 style='margin-bottom:0;'>{APP_NAME}</h2>", unsafe_allow_html=True)
                st.caption(COMPANY_NAME)

            # Separator
            st.markdown("---")

            # Navigation sections
            for section in NAVIGATION:
                st.subheader(section["section"])

                for item in section["items"]:
                    # Highlight the current page
                    is_active = st.session_state.get("page") == item["page"]

                    # Custom styling for active button
                    if is_active:
                        button_style = f"""
                        <style>
                        div[data-testid="stHorizontalBlock"]:has(button#{item["page"]}) {{
                            background-color: rgba(30, 136, 229, 0.1);
                            border-left: 3px solid {PRIMARY_COLOR};
                            border-radius: 5px;
                        }}
                        </style>
                        """
                        st.markdown(button_style, unsafe_allow_html=True)

                    # Create a button with the item name
                    if st.button(
                        f"{item['icon']} {item['name']}",
                        key=item["page"],
                        use_container_width=True
                    ):
                        st.session_state.page = item["page"]
                        # Force a rerun to update the UI
                        st.experimental_rerun()

                # Add a small space after each section
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

            # Separator
            st.markdown("---")

            # User section
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    # User avatar (placeholder)
                    st.markdown(
                        f"""
                        <div style="width:40px;height:40px;border-radius:50%;background-color:{PRIMARY_COLOR};
                        display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">
                        A
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown("<b>Administrator</b>", unsafe_allow_html=True)
                    st.caption("admin@hvacsolutions.com")

            # User actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ Ustawienia", use_container_width=True):
                    # Placeholder for settings functionality
                    st.session_state.show_settings = True

            with col2:
                if st.button("🚪 Wyloguj", use_container_width=True):
                    # Placeholder for logout functionality
                    st.session_state.clear()
                    st.experimental_rerun()

            # Version and system info
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            st.caption(f"Wersja: 1.0.0 | {datetime.now().strftime('%Y-%m-%d')}")

            # System status indicator
            system_status = "online"  # This could be dynamic based on backend checks
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;margin-top:5px;">
                    <div style="width:8px;height:8px;border-radius:50%;background-color:{'green' if system_status == 'online' else 'red'};margin-right:5px;"></div>
                    <span style="font-size:0.8rem;">System {system_status}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        logger.error(f"Error rendering sidebar: {e}")
        # Fallback to a simpler sidebar if there's an error
        with st.sidebar:
            st.title(APP_NAME)
            st.caption(COMPANY_NAME)
            st.markdown("---")

            if st.button("📊 Panel główny"):
                st.session_state.page = "dashboard"

            if st.button("👥 Klienci"):
                st.session_state.page = "clients"

def initialize_session_state():
    """Initialize session state variables."""
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # Initialize other session state variables
    if "user" not in st.session_state:
        st.session_state.user = {
            "id": 1,
            "name": "Administrator",
            "email": "admin@hvacsolutions.com",
            "role": "admin"
        }

    # Initialize feature flags
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
