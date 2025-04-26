import streamlit as st
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components and pages
from components.sidebar import render_sidebar, initialize_session_state
from pages import dashboard, clients, devices, buildings, service_orders

# Configure the Streamlit page
st.set_page_config(
    page_title="HVAC CRM/ERP System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
def add_custom_css():
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        h1, h2, h3 {
            color: #1E88E5;
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
            background-color: #1E88E5;
            color: white;
        }
        
        div[data-testid="stExpander"] div[role="button"] p {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {
            background-color: #F8F9FA;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        div[data-testid="metric-container"] {
            background-color: #F8F9FA;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        div[data-testid="metric-container"] label {
            color: #424242;
        }
        
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #1E88E5;
        }
        
        div[data-testid="stDataFrame"] {
            border-radius: 5px;
            overflow: hidden;
        }
        
        button[kind="primary"] {
            background-color: #1E88E5;
            color: white;
        }
        
        button[kind="secondary"] {
            border: 1px solid #1E88E5;
            color: #1E88E5;
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
        </style>
    """, unsafe_allow_html=True)

def main():
    # Add custom CSS
    add_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render the appropriate page based on session state
    if st.session_state.page == "dashboard":
        dashboard.render()
    elif st.session_state.page == "clients":
        clients.render()
    elif st.session_state.page == "devices":
        # Placeholder for devices page
        st.title("🔧 Urządzenia")
        st.info("Strona urządzeń jest w trakcie implementacji.")
    elif st.session_state.page == "buildings":
        # Placeholder for buildings page
        st.title("🏢 Budynki/Lokalizacje")
        st.info("Strona budynków jest w trakcie implementacji.")
    elif st.session_state.page == "service_orders":
        # Placeholder for service orders page
        st.title("📋 Zlecenia serwisowe")
        st.info("Strona zleceń serwisowych jest w trakcie implementacji.")
    elif st.session_state.page == "calendar":
        # Placeholder for calendar page
        st.title("📅 Kalendarz")
        st.info("Strona kalendarza jest w trakcie implementacji.")
    elif st.session_state.page == "offers_invoices":
        # Placeholder for offers and invoices page
        st.title("💰 Oferty i faktury")
        st.info("Strona ofert i faktur jest w trakcie implementacji.")
    elif st.session_state.page == "inventory":
        # Placeholder for inventory page
        st.title("📦 Magazyn części")
        st.info("Strona magazynu części jest w trakcie implementacji.")
    elif st.session_state.page == "reports":
        # Placeholder for reports page
        st.title("📈 Raporty")
        st.info("Strona raportów jest w trakcie implementacji.")
    elif st.session_state.page == "communication":
        # Placeholder for communication page
        st.title("✉️ Komunikacja")
        st.info("Strona komunikacji jest w trakcie implementacji.")
    elif st.session_state.page == "visualizations":
        # Placeholder for visualizations page
        st.title("🖼️ Wizualizacje/zdjęcia")
        st.info("Strona wizualizacji jest w trakcie implementacji.")
    elif st.session_state.page == "automation":
        # Placeholder for automation page
        st.title("⚙️ Automatyzacja/procesy")
        st.info("Strona automatyzacji jest w trakcie implementacji.")
    elif st.session_state.page == "client_portal":
        # Placeholder for client portal page
        st.title("🌐 Panel klienta")
        st.info("Strona panelu klienta jest w trakcie implementacji.")
    else:
        # Default to dashboard
        dashboard.render()

if __name__ == "__main__":
    main()
