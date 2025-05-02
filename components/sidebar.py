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
            # Logo and app name with improved styling
            col1, col2 = st.columns([1, 3])
            with col1:
                if os.path.exists(LOGO_PATH):
                    st.image(LOGO_PATH, width=60)
                else:
                    # Fallback icon if logo doesn't exist
                    st.markdown(f"""
                        <div style="width:60px;height:60px;border-radius:10px;background-color:{PRIMARY_COLOR};
                        display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:24px;">
                        HVAC
                        </div>
                    """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"<h2 style='margin-bottom:0;color:{PRIMARY_COLOR};'>{APP_NAME}</h2>", unsafe_allow_html=True)
                st.caption(f"<span style='font-weight:500;'>{COMPANY_NAME}</span>", unsafe_allow_html=True)

            # Separator with improved styling
            st.markdown(f"<hr style='margin:10px 0;border:none;height:1px;background-color:#e0e0e0;'>", unsafe_allow_html=True)

            # Search box for quick navigation
            st.text_input("🔍 Szukaj...", placeholder="Szukaj funkcji...", key="sidebar_search")

            # Navigation sections with improved styling
            for section in NAVIGATION:
                st.markdown(f"<h4 style='margin-bottom:5px;margin-top:15px;color:#424242;'>{section['section']}</h4>", unsafe_allow_html=True)

                for item in section["items"]:
                    # Highlight the current page
                    is_active = st.session_state.get("page") == item["page"]

                    # Custom styling for active and hover states
                    button_style = f"""
                    <style>
                    div[data-testid="stHorizontalBlock"]:has(button#{item["page"]}) {{
                        background-color: {f"rgba(30, 136, 229, 0.1)" if is_active else "transparent"};
                        border-left: {f"3px solid {PRIMARY_COLOR}" if is_active else "3px solid transparent"};
                        border-radius: 5px;
                        transition: all 0.2s ease;
                        margin-bottom: 2px;
                    }}
                    div[data-testid="stHorizontalBlock"]:has(button#{item["page"]}):hover {{
                        background-color: rgba(30, 136, 229, 0.05);
                    }}
                    button#{item["page"]} {{
                        font-weight: {500 if is_active else 400};
                        color: {PRIMARY_COLOR if is_active else "#424242"};
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
                        st.rerun()

            # Separator
            st.markdown(f"<hr style='margin:20px 0 15px 0;border:none;height:1px;background-color:#e0e0e0;'>", unsafe_allow_html=True)

            # User section with improved styling
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    # User avatar with improved styling
                    st.markdown(
                        f"""
                        <div style="width:45px;height:45px;border-radius:50%;background-color:{PRIMARY_COLOR};
                        display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;
                        box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                        A
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(f"<b style='color:#212121;'>Administrator</b>", unsafe_allow_html=True)
                    st.caption(f"<span style='color:#616161;'>admin@hvacsolutions.com</span>", unsafe_allow_html=True)

            # User actions with improved styling
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ Ustawienia", use_container_width=True, key="settings_btn"):
                    # Placeholder for settings functionality
                    st.session_state.show_settings = True

            with col2:
                if st.button("🚪 Wyloguj", use_container_width=True, key="logout_btn"):
                    # Placeholder for logout functionality
                    st.session_state.clear()
                    st.rerun()

            # Version and system info with improved styling
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            st.caption(f"<span style='color:#757575;'>Wersja: 1.0.0 | {datetime.now().strftime('%Y-%m-%d')}</span>", unsafe_allow_html=True)

            # System status indicator with improved styling
            system_status = "online"  # This could be dynamic based on backend checks
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;margin-top:5px;">
                    <div style="width:8px;height:8px;border-radius:50%;background-color:{'#4CAF50' if system_status == 'online' else '#F44336'};margin-right:5px;box-shadow:0 0 5px {'rgba(76, 175, 80, 0.5)' if system_status == 'online' else 'rgba(244, 67, 54, 0.5)'}"></div>
                    <span style="font-size:0.8rem;color:#757575;">System {system_status}</span>
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
