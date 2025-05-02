import streamlit as st
import os
import sys
import logging
import traceback
from datetime import datetime, timedelta
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
    from pages import dashboard, clients, communication, voice_interface
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
        st.markdown(f"""
            <style>
            /* Main container styling */
            .main .block-container {{
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
                max-width: 1200px;
            }}
            
            /* Typography improvements */
            h1, h2, h3 {{
                color: {PRIMARY_COLOR};
                font-weight: 600;
                margin-bottom: 1rem;
            }}
            
            h1 {{
                font-size: 2rem;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 0.5rem;
                margin-bottom: 1.5rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
                margin-top: 1.5rem;
            }}
            
            h3 {{
                font-size: 1.2rem;
                margin-top: 1rem;
            }}
            
            p {{
                line-height: 1.6;
                color: #424242;
            }}
            
            /* Tabs styling */
            .stTabs {{
                margin-top: 1rem;
            }}
            
            .stTabs [data-baseweb="tab-list"] {{
                gap: 2px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 45px;
                white-space: pre-wrap;
                background-color: #F8F9FA;
                border-radius: 6px 6px 0px 0px;
                gap: 1px;
                padding: 8px 16px;
                font-weight: 500;
                transition: all 0.2s ease;
                border: 1px solid #e0e0e0;
                border-bottom: none;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                background-color: #F0F2F6;
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: 1px solid {PRIMARY_COLOR};
                border-bottom: none;
                box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
            }}
            
            /* Expander styling */
            div[data-testid="stExpander"] {{
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-bottom: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            
            div[data-testid="stExpander"] div[role="button"] {{
                padding: 1rem;
            }}
            
            div[data-testid="stExpander"] div[role="button"] p {{
                font-size: 1.05rem;
                font-weight: 600;
                color: #212121;
                margin: 0;
            }}
            
            /* Card-like containers */
            div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {{
                background-color: {BACKGROUND_COLOR};
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: all 0.2s ease;
            }}
            
            div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"]:hover {{
                box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            }}
            
            /* Metric containers */
            div[data-testid="metric-container"] {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                border: 1px solid #e0e0e0;
                transition: all 0.2s ease;
            }}
            
            div[data-testid="metric-container"]:hover {{
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }}
            
            div[data-testid="metric-container"] label {{
                color: #616161;
                font-weight: 500;
                font-size: 0.9rem;
            }}
            
            div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
                color: {PRIMARY_COLOR};
                font-weight: 600;
                font-size: 1.8rem;
            }}
            
            div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {{
                font-size: 0.9rem;
            }}
            
            /* DataFrame styling */
            div[data-testid="stDataFrame"] {{
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            
            div[data-testid="stDataFrame"] th {{
                background-color: #f5f5f5;
                color: #424242;
                font-weight: 600;
                padding: 10px;
            }}
            
            div[data-testid="stDataFrame"] td {{
                padding: 8px 10px;
            }}
            
            /* Button styling */
            button[kind="primary"] {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border-radius: 8px;
                font-weight: 600;
                padding: 0.6rem 1.2rem;
                transition: all 0.3s ease;
                border: none;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.9rem;
            }}
            
            button[kind="primary"]:hover {{
                background-color: {PRIMARY_COLOR}e0;
                box-shadow: 0 6px 10px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }}
            
            button[kind="secondary"] {{
                border: 2px solid {PRIMARY_COLOR};
                color: {PRIMARY_COLOR};
                border-radius: 8px;
                font-weight: 600;
                padding: 0.6rem 1.2rem;
                transition: all 0.3s ease;
                background-color: white;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.9rem;
            }}
            
            button[kind="secondary"]:hover {{
                background-color: {PRIMARY_COLOR}10;
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            /* Standard Streamlit buttons */
            .stButton > button {{
                border-radius: 8px;
                font-weight: 500;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
                border: 1px solid #e0e0e0;
                background-color: white;
                color: #424242;
            }}
            
            .stButton > button:hover {{
                border-color: {PRIMARY_COLOR};
                color: {PRIMARY_COLOR};
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }}
            
            /* Card styling */
            .card {{
                background-color: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 8px 16px rgba(0,0,0,0.05);
                margin-bottom: 1.5rem;
                border: 1px solid #f0f0f0;
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                box-shadow: 0 12px 20px rgba(0,0,0,0.1);
                transform: translateY(-5px);
                border-color: #e0e0e0;
            }}
            
            /* Card header */
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid #f0f0f0;
            }}
            
            .card-header h3 {{
                margin: 0;
                color: #212121;
                font-weight: 600;
            }}
            
            /* Sidebar styling */
            .stSidebar {{
                background-color: white;
                border-right: 1px solid #e0e0e0;
                box-shadow: 2px 0 10px rgba(0,0,0,0.05);
            }}
            
            .stSidebar [data-testid="stVerticalBlock"] {{
                gap: 0.5rem;
            }}
            
            .stSidebar button {{
                text-align: left;
                border: none;
                background-color: transparent;
                transition: all 0.3s ease;
                border-radius: 6px;
                padding: 0.6rem 0.75rem;
                font-weight: 500;
                color: #424242;
            }}
            
            .stSidebar button:hover {{
                background-color: rgba(30, 136, 229, 0.1);
                transform: translateX(3px);
                color: {PRIMARY_COLOR};
            }}
            
            /* Sidebar section headers */
            .stSidebar h4 {{
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #757575;
                margin-top: 20px;
                margin-bottom: 8px;
                padding-left: 10px;
                border-left: 3px solid {PRIMARY_COLOR};
            }}
            
            /* Input fields styling */
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea {{
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                padding: 0.5rem;
                transition: all 0.2s ease;
            }}
            
            div[data-baseweb="input"] input:focus,
            div[data-baseweb="textarea"] textarea:focus {{
                border-color: {PRIMARY_COLOR};
                box-shadow: 0 0 0 2px {PRIMARY_COLOR}30;
            }}
            
            /* Select box styling */
            div[data-baseweb="select"] {{
                border-radius: 6px;
                transition: all 0.2s ease;
            }}
            
            div[data-baseweb="select"]:focus-within {{
                border-color: {PRIMARY_COLOR};
                box-shadow: 0 0 0 2px {PRIMARY_COLOR}30;
            }}
            
            /* Loading spinner customization */
            div.stSpinner > div {{
                border-top-color: {PRIMARY_COLOR} !important;
            }}
            
            /* Info/warning/error boxes */
            div[data-testid="stAlert"] {{
                border-radius: 6px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left-width: 4px;
            }}
            
            /* Footer styling */
            footer {{
                visibility: hidden;
            }}
            
            .custom-footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: white;
                padding: 8px 15px;
                text-align: center;
                font-size: 0.8rem;
                border-top: 1px solid #e0e0e0;
                color: #757575;
                z-index: 1000;
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {{
                .main .block-container {{
                    padding: 1rem;
                }}
                
                div[data-testid="metric-container"] {{
                    padding: 15px;
                }}
                
                h1 {{
                    font-size: 1.5rem;
                }}
                
                h2 {{
                    font-size: 1.3rem;
                }}
            }}
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
                <div style="display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:0 auto;">
                    <div>
                        {APP_NAME} <span style="color:{PRIMARY_COLOR};font-weight:500;">v1.0.0</span>
                    </div>
                    <div>
                        © {datetime.now().year} {COMPANY_NAME} | Wszelkie prawa zastrzeżone
                    </div>
                    <div>
                        <a href="#" style="color:{PRIMARY_COLOR};text-decoration:none;margin-left:10px;">Pomoc</a>
                        <a href="#" style="color:{PRIMARY_COLOR};text-decoration:none;margin-left:10px;">Kontakt</a>
                    </div>
                </div>
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

    # Otherwise, render a placeholder with improved styling
    page_titles = {
        "devices": "🔧 Urządzenia",
        "buildings": "🏢 Budynki/Lokalizacje",
        "service_orders": "📋 Zlecenia serwisowe",
        "calendar": "📅 Kalendarz",
        "offers_invoices": "💰 Oferty i faktury",
        "inventory": "📦 Magazyn części",
        "reports": "📈 Raporty",
        "visualizations": "🖼️ Wizualizacje/zdjęcia",
        "automation": "⚙️ Automatyzacja/procesy",
        "client_portal": "🌐 Panel klienta"
    }

    title = page_titles.get(page, "📊 Panel główny")
    st.title(title)

    # Show a more professional "coming soon" message with improved styling
    with st.container():
        # Progress data
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
        
        # Custom coming soon message with progress indicator
        st.markdown(f"""
            <div style="background-color:#f8f9fa;padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;border:1px solid #e0e0e0;">
                <img src="https://cdn.streamlit.io/images/coding.svg" width="150" style="margin-bottom:15px;">
                <h2 style="margin-bottom:10px;color:#424242;">Funkcjonalność w trakcie rozwoju</h2>
                <p style="margin-bottom:20px;color:#616161;font-size:1.1rem;">
                    Ta część systemu jest obecnie w fazie rozwoju. Pracujemy nad jej wdrożeniem, aby zapewnić najlepsze doświadczenie użytkownika.
                </p>
                <div style="max-width:400px;margin:0 auto;">
                    <div style="height:10px;background-color:#e0e0e0;border-radius:5px;margin-bottom:5px;">
                        <div style="height:10px;width:{progress}%;background-color:{PRIMARY_COLOR};border-radius:5px;"></div>
                    </div>
                    <p style="text-align:right;margin:0;color:#757575;">Postęp: {progress}%</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Add estimated completion date based on progress
        if progress < 100:
            # Calculate estimated completion date (just for display purposes)
            days_remaining = int((100 - progress) / 5)  # Rough estimate: 5% progress per day
            completion_date = (datetime.now() + timedelta(days=days_remaining)).strftime("%d.%m.%Y")
            
            st.markdown(f"""
                <div style="text-align:center;margin-bottom:20px;">
                    <p style="color:#616161;">Szacowana data ukończenia: <span style="font-weight:500;color:#212121;">{completion_date}</span></p>
                </div>
            """, unsafe_allow_html=True)
        
        # Add feature preview or description based on the page
        feature_descriptions = {
            "devices": "Zarządzaj urządzeniami HVAC, śledź ich status, historię serwisową i parametry techniczne. Planuj przeglądy i otrzymuj powiadomienia o potencjalnych problemach.",
            "buildings": "Organizuj lokalizacje i budynki klientów, przypisuj do nich urządzenia i monitoruj warunki środowiskowe w różnych strefach.",
            "service_orders": "Twórz i zarządzaj zleceniami serwisowymi, przydzielaj techników, śledź postęp prac i generuj raporty z wykonanych usług.",
            "calendar": "Planuj wizyty serwisowe, przeglądy i inne wydarzenia. Synchronizuj kalendarz z urządzeniami mobilnymi techników.",
            "offers_invoices": "Twórz oferty i faktury dla klientów, śledź płatności i generuj raporty finansowe.",
            "inventory": "Zarządzaj częściami zamiennymi, śledź stany magazynowe i automatycznie generuj zamówienia przy niskich stanach.",
            "reports": "Generuj zaawansowane raporty i analizy dotyczące wydajności systemu, pracy techników i satysfakcji klientów.",
            "visualizations": "Przeglądaj zdjęcia, schematy i wizualizacje 3D instalacji HVAC. Dodawaj adnotacje i udostępniaj je klientom.",
            "automation": "Konfiguruj automatyczne procesy i powiadomienia w oparciu o dane z urządzeń i harmonogramy przeglądów.",
            "client_portal": "Udostępniaj klientom dedykowany portal do monitorowania ich urządzeń, zgłaszania problemów i przeglądania historii serwisowej."
        }
        
        if page in feature_descriptions:
            st.markdown(f"""
                <div style="background-color:white;padding:20px;border-radius:8px;margin-top:20px;border:1px solid #e0e0e0;">
                    <h3 style="margin-bottom:10px;color:{PRIMARY_COLOR};">Co będzie dostępne w tej sekcji?</h3>
                    <p style="color:#424242;line-height:1.6;">{feature_descriptions.get(page)}</p>
                </div>
            """, unsafe_allow_html=True)
            
        # Add a button to go back to dashboard
        st.markdown("<div style='margin-top:30px;text-align:center;'>", unsafe_allow_html=True)
        if st.button("↩️ Powrót do panelu głównego", use_container_width=False):
            st.session_state.page = "dashboard"
            st.rerun()

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
