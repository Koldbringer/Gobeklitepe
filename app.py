import streamlit as st
import os
import sys
import logging
import traceback
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components and pages
try:
    from components.sidebar import render_sidebar, initialize_session_state
    from pages import dashboard, clients, devices, buildings, service_orders, communication, voice_interface
    from components import quantum_visualization
    from services import quantum_communication, voice_communication
    from config import APP_NAME, COMPANY_NAME, PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    logger.error(traceback.format_exc())
    raise

# Performance monitoring
start_time = time.time()

# Configure the Streamlit page
try:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'mailto:support@hvacsolutions.com',
            'Report a bug': 'mailto:bugs@hvacsolutions.com',
            'About': f"{APP_NAME} - Version 1.0.0 - © {datetime.now().year} {COMPANY_NAME}"
        }
    )
    logger.info(f"Page config set up in {time.time() - start_time:.2f} seconds")
except Exception as e:
    logger.error(f"Error setting page config: {e}")
    logger.error(traceback.format_exc())
    st.error("Error setting up application. Please contact support.")

# Add custom CSS
def add_custom_css():
    try:
        st.markdown("""
            <style>
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            h1, h2, h3 {
                color: """ + PRIMARY_COLOR + """;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
            }

            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #F0F2F6;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }

            .stTabs [aria-selected="true"] {
                background-color: """ + PRIMARY_COLOR + """;
                color: white;
            }

            div[data-testid="stExpander"] div[role="button"] p {
                font-size: 1.1rem;
                font-weight: 600;
            }

            div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
                background-color: """ + BACKGROUND_COLOR + """;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }

            div[data-testid="metric-container"] {
                background-color: """ + BACKGROUND_COLOR + """;
                border-radius: 5px;
                padding: 15px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }

            div[data-testid="metric-container"] label {
                color: #424242;
            }

            div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
                color: """ + PRIMARY_COLOR + """;
            }

            div[data-testid="stDataFrame"] {
                border-radius: 5px;
                overflow: hidden;
            }

            button[kind="primary"] {
                background-color: """ + PRIMARY_COLOR + """;
                color: white;
            }

            button[kind="secondary"] {
                border: 1px solid """ + PRIMARY_COLOR + """;
                color: """ + PRIMARY_COLOR + """;
            }

            .stSidebar [data-testid="stVerticalBlock"] {
                gap: 0.5rem;
            }

            .stSidebar button {
                text-align: left;
                border: none;
                background-color: transparent;
                transition: background-color 0.2s;
            }

            .stSidebar button:hover {
                background-color: rgba(30, 136, 229, 0.1);
            }

            /* Loading spinner customization */
            div.stSpinner > div {
                border-top-color: """ + PRIMARY_COLOR + """ !important;
            }

            /* Footer styling */
            footer {
                visibility: hidden;
            }
            .custom-footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: """ + BACKGROUND_COLOR + """;
                padding: 5px 10px;
                text-align: center;
                font-size: 0.8rem;
                border-top: 1px solid #e0e0e0;
            }

            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .main .block-container {
                    padding: 1rem;
                }
                div[data-testid="metric-container"] {
                    padding: 10px;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        logger.info(f"Custom CSS added in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error adding custom CSS: {e}")
        logger.error(traceback.format_exc())

def render_footer():
    """Render a custom footer with version and copyright information."""
    try:
        st.markdown(
            f"""
            <div class="custom-footer">
                {APP_NAME} v1.0.0 | © {datetime.now().year} {COMPANY_NAME} | Wszelkie prawa zastrzeżone
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        logger.error(f"Error rendering footer: {e}")

def handle_error(func):
    """Decorator to handle errors in page rendering."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            st.error(f"Wystąpił błąd podczas ładowania strony. Spróbuj odświeżyć stronę lub skontaktuj się z administratorem.")
            with st.expander("Szczegóły błędu (dla administratora)"):
                st.code(traceback.format_exc())
    return wrapper

@handle_error
def render_page():
    """Render the appropriate page based on session state."""
    page = st.session_state.get("page", "dashboard")

    # Dictionary mapping page names to their render functions
    page_map = {
        "dashboard": dashboard.render,
        "clients": clients.render,
        "communication": communication.render,
        "voice_interface": voice_interface.render,
        "quantum_dashboard": quantum_visualization.render_quantum_communication_dashboard,
    }

    # If the page has a render function, call it
    if page in page_map:
        page_map[page]()
        return

    # Otherwise, render a placeholder
    page_titles = {
        "devices": "🔧 Urządzenia",
        "buildings": "🏢 Budynki/Lokalizacje",
        "service_orders": "📋 Zlecenia serwisowe",
        "calendar": "📅 Kalendarz",
        "offers_invoices": "💰 Oferty i faktury",
        "inventory": "📦 Magazyn części",
        "reports": "📈 Raporty",
        "communication": "✉️ Komunikacja",
        "visualizations": "🖼️ Wizualizacje/zdjęcia",
        "automation": "⚙️ Automatyzacja/procesy",
        "client_portal": "🌐 Panel klienta"
    }

    title = page_titles.get(page, "📊 Panel główny")
    st.title(title)

    # Show a more professional "coming soon" message
    with st.container():
        st.info(f"Ta funkcjonalność będzie dostępna wkrótce. Pracujemy nad jej wdrożeniem.")

        # Add a progress bar to show development progress
        progress = {
            "devices": 60,
            "buildings": 50,
            "service_orders": 70,
            "calendar": 40,
            "offers_invoices": 30,
            "inventory": 20,
            "reports": 10,
            "communication": 100,  # Communication page is now fully implemented
            "voice_interface": 100,  # Voice interface is now fully implemented
            "quantum_dashboard": 100,  # Quantum dashboard is now fully implemented
            "visualizations": 25,
            "automation": 5,
            "client_portal": 35
        }.get(page, 0)

        if progress > 0:
            st.progress(progress/100)
            st.caption(f"Postęp implementacji: {progress}%")

def main():
    try:
        # Add custom CSS
        add_custom_css()

        # Initialize session state
        initialize_session_state()

        # Render sidebar
        render_sidebar()

        # Render the appropriate page
        render_page()

        # Render footer
        render_footer()

        # Log performance metrics
        end_time = time.time()
        logger.info(f"Page rendered in {end_time - start_time:.2f} seconds")

    except Exception as e:
        logger.error(f"Unhandled error in main: {e}")
        logger.error(traceback.format_exc())
        st.error("Wystąpił nieoczekiwany błąd. Prosimy odświeżyć stronę lub skontaktować się z administratorem.")
        with st.expander("Szczegóły błędu (dla administratora)"):
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
