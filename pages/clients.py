import streamlit as st
import pandas as pd
from utils import db
import plotly.express as px

def render():
    """Render the clients page."""
    st.title("👥 Klienci")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Lista klientów", "Dodaj klienta", "Analiza"])
    
    with tab1:
        render_client_list()
    
    with tab2:
        render_add_client_form()
    
    with tab3:
        render_client_analysis()

def render_client_list():
    """Render the client list view."""
    # Search and filter options
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        search = st.text_input("Szukaj klienta", placeholder="Nazwa, email lub telefon...")
    
    with col2:
        client_type = st.selectbox(
            "Typ klienta",
            options=["Wszyscy", "indywidualny", "biznesowy"],
            index=0
        )
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        refresh = st.button("Odśwież")
    
    # Get clients from database
    clients = db.get_clients(search=search if search else None)
    
    # Filter by client type if selected
    if client_type != "Wszyscy" and clients:
        clients = [c for c in clients if c.get('typ_klienta') == client_type]
    
    # Display clients
    if clients:
        # Convert to DataFrame for easier display
        df_clients = pd.DataFrame(clients)
        
        # Format the DataFrame for display
        display_df = df_clients[['id', 'nazwa', 'email', 'telefon', 'typ_klienta', 'data_rejestracji']]
        display_df.columns = ['ID', 'Nazwa', 'Email', 'Telefon', 'Typ', 'Data rejestracji']
        
        # Add action buttons using Streamlit's experimental data editor
        st.dataframe(display_df, use_container_width=True)
        
        # Allow selecting a client for details
        selected_client_id = st.selectbox(
            "Wybierz klienta, aby zobaczyć szczegóły:",
            options=[client['id'] for client in clients],
            format_func=lambda x: f"{next((client['nazwa'] for client in clients if client['id'] == x), '')}"
        )
        
        if selected_client_id:
            display_client_details(selected_client_id)
    else:
        st.info("Brak klientów spełniających kryteria wyszukiwania.")

def display_client_details(client_id):
    """Display details for a selected client."""
    client = db.get_client_by_id(client_id)
    
    if client:
        with st.expander("Szczegóły klienta", expanded=True):
            # Client info in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(client['nazwa'])
                st.write(f"**Email:** {client['email'] or 'Brak'}")
                st.write(f"**Telefon:** {client['telefon'] or 'Brak'}")
                st.write(f"**Adres:** {client['adres'] or 'Brak'}")
            
            with col2:
                st.write(f"**Typ klienta:** {client['typ_klienta'] or 'Nie określono'}")
                st.write(f"**Data rejestracji:** {client['data_rejestracji']}")
                st.write(f"**Ostatni kontakt:** {client['ostatni_kontakt'] or 'Brak'}")
                st.write(f"**Ocena zamożności:** {client['ocena_zamożności'] or 'Nie określono'}")
            
            # Notatki
            st.write("**Notatki:**")
            st.write(client['notatki'] or "Brak notatek")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Edytuj", key="edit_client"):
                    # Set session state for editing
                    st.session_state.edit_client_id = client_id
                    st.experimental_rerun()
            
            with col2:
                if st.button("Nowe zlecenie", key="new_order"):
                    # Navigate to service orders page with client pre-selected
                    st.session_state.page = "service_orders"
                    st.session_state.new_order_client_id = client_id
            
            with col3:
                if st.button("Nowa oferta", key="new_offer"):
                    # Navigate to offers page with client pre-selected
                    st.session_state.page = "offers_invoices"
                    st.session_state.new_offer_client_id = client_id
            
            with col4:
                if st.button("Wyślij email", key="send_email"):
                    # Navigate to communication page with client pre-selected
                    st.session_state.page = "communication"
                    st.session_state.email_client_id = client_id
            
            # Tabs for related information
            client_tabs = st.tabs(["Urządzenia", "Budynki", "Zlecenia", "Komunikacja", "Dokumenty"])
            
            with client_tabs[0]:
                # Get devices for this client
                devices = db.get_devices(client_id=client_id)
                
                if devices:
                    # Convert to DataFrame for display
                    df_devices = pd.DataFrame(devices)
                    display_df = df_devices[['id', 'model', 'numer_seryjny', 'data_instalacji', 'status']]
                    display_df.columns = ['ID', 'Model', 'Numer seryjny', 'Data instalacji', 'Status']
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    if st.button("Dodaj urządzenie", key="add_device"):
                        # Navigate to devices page with client pre-selected
                        st.session_state.page = "devices"
                        st.session_state.new_device_client_id = client_id
                else:
                    st.info("Brak urządzeń dla tego klienta.")
                    
                    if st.button("Dodaj pierwsze urządzenie", key="add_first_device"):
                        # Navigate to devices page with client pre-selected
                        st.session_state.page = "devices"
                        st.session_state.new_device_client_id = client_id
            
            with client_tabs[1]:
                # Get buildings for this client
                buildings = db.get_buildings(client_id=client_id)
                
                if buildings:
                    # Convert to DataFrame for display
                    df_buildings = pd.DataFrame(buildings)
                    display_df = df_buildings[['id', 'nazwa', 'adres', 'typ_budynku']]
                    display_df.columns = ['ID', 'Nazwa', 'Adres', 'Typ']
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    if st.button("Dodaj budynek", key="add_building"):
                        # Navigate to buildings page with client pre-selected
                        st.session_state.page = "buildings"
                        st.session_state.new_building_client_id = client_id
                else:
                    st.info("Brak budynków dla tego klienta.")
                    
                    if st.button("Dodaj pierwszy budynek", key="add_first_building"):
                        # Navigate to buildings page with client pre-selected
                        st.session_state.page = "buildings"
                        st.session_state.new_building_client_id = client_id
            
            with client_tabs[2]:
                # Get service orders for this client
                orders = db.get_service_orders(client_id=client_id)
                
                if orders:
                    # Convert to DataFrame for display
                    df_orders = pd.DataFrame(orders)
                    display_df = df_orders[['id', 'typ_zlecenia', 'status', 'data_utworzenia', 'data_planowana']]
                    display_df.columns = ['ID', 'Typ', 'Status', 'Data utworzenia', 'Data planowana']
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    if st.button("Nowe zlecenie serwisowe", key="add_service_order"):
                        # Navigate to service orders page with client pre-selected
                        st.session_state.page = "service_orders"
                        st.session_state.new_order_client_id = client_id
                else:
                    st.info("Brak zleceń serwisowych dla tego klienta.")
                    
                    if st.button("Dodaj pierwsze zlecenie", key="add_first_order"):
                        # Navigate to service orders page with client pre-selected
                        st.session_state.page = "service_orders"
                        st.session_state.new_order_client_id = client_id
            
            with client_tabs[3]:
                # Placeholder for communication history
                st.info("Historia komunikacji w trakcie implementacji.")
                
                # Sample communication history
                st.write("**Ostatnie wiadomości:**")
                
                sample_messages = [
                    {"date": "2023-05-15", "type": "Email", "subject": "Oferta na serwis klimatyzacji"},
                    {"date": "2023-05-10", "type": "Telefon", "subject": "Rozmowa o awarii urządzenia"},
                    {"date": "2023-04-22", "type": "SMS", "subject": "Przypomnienie o przeglądzie"}
                ]
                
                for msg in sample_messages:
                    st.write(f"{msg['date']} | {msg['type']} | {msg['subject']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Wyślij wiadomość", key="send_message"):
                        # Navigate to communication page
                        st.session_state.page = "communication"
                        st.session_state.message_client_id = client_id
                
                with col2:
                    if st.button("Zobacz całą historię", key="view_history"):
                        # Navigate to communication page with history view
                        st.session_state.page = "communication"
                        st.session_state.view_history_client_id = client_id
            
            with client_tabs[4]:
                # Placeholder for documents
                st.info("Dokumenty w trakcie implementacji.")
                
                # Sample documents
                st.write("**Dokumenty klienta:**")
                
                sample_docs = [
                    {"date": "2023-06-01", "type": "Faktura", "name": "FV/2023/06/001"},
                    {"date": "2023-05-15", "type": "Oferta", "name": "OF/2023/05/001"},
                    {"date": "2023-04-10", "type": "Umowa", "name": "UM/2023/04/001"}
                ]
                
                for doc in sample_docs:
                    st.write(f"{doc['date']} | {doc['type']} | {doc['name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Dodaj dokument", key="add_document"):
                        # Placeholder for adding document
                        st.info("Funkcjonalność dodawania dokumentów w trakcie implementacji.")
                
                with col2:
                    if st.button("Skanuj dokument (OCR)", key="scan_document"):
                        # Placeholder for OCR scanning
                        st.info("Funkcjonalność OCR w trakcie implementacji.")

def render_add_client_form():
    """Render the form for adding a new client."""
    st.subheader("Dodaj nowego klienta")
    
    # Client form
    with st.form("add_client_form"):
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            nazwa = st.text_input("Nazwa klienta *", placeholder="Imię i nazwisko lub nazwa firmy")
            email = st.text_input("Email", placeholder="email@example.com")
            telefon = st.text_input("Telefon", placeholder="+48 123 456 789")
        
        with col2:
            typ_klienta = st.selectbox(
                "Typ klienta",
                options=["indywidualny", "biznesowy"],
                index=0
            )
            ocena_zamożności = st.slider(
                "Ocena zamożności",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5
            )
        
        # Address
        adres = st.text_area("Adres", placeholder="Ulica, numer, kod pocztowy, miasto")
        
        # Notes
        notatki = st.text_area("Notatki", placeholder="Dodatkowe informacje o kliencie...")
        
        # Submit button
        submitted = st.form_submit_button("Dodaj klienta")
        
        if submitted:
            if not nazwa:
                st.error("Nazwa klienta jest wymagana.")
            else:
                # Prepare client data
                client_data = {
                    "nazwa": nazwa,
                    "email": email if email else None,
                    "telefon": telefon if telefon else None,
                    "adres": adres if adres else None,
                    "typ_klienta": typ_klienta,
                    "ocena_zamożności": ocena_zamożności,
                    "notatki": notatki if notatki else None
                }
                
                # Create client in database
                client_id = db.create_client(client_data)
                
                if client_id:
                    st.success(f"Klient '{nazwa}' został dodany pomyślnie!")
                    
                    # Option to add more details
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Dodaj budynek"):
                            # Navigate to buildings page with client pre-selected
                            st.session_state.page = "buildings"
                            st.session_state.new_building_client_id = client_id
                    
                    with col2:
                        if st.button("Dodaj urządzenie"):
                            # Navigate to devices page with client pre-selected
                            st.session_state.page = "devices"
                            st.session_state.new_device_client_id = client_id
                    
                    with col3:
                        if st.button("Dodaj zlecenie"):
                            # Navigate to service orders page with client pre-selected
                            st.session_state.page = "service_orders"
                            st.session_state.new_order_client_id = client_id
                else:
                    st.error("Wystąpił błąd podczas dodawania klienta.")

def render_client_analysis():
    """Render client analysis view."""
    st.subheader("Analiza klientów")
    
    # Sample data for analysis
    # In a real application, this would come from the database
    
    # Client types distribution
    st.write("**Rozkład typów klientów**")
    
    client_types_data = {
        'Typ': ['indywidualny', 'biznesowy'],
        'Liczba': [65, 35]
    }
    
    df_types = pd.DataFrame(client_types_data)
    
    fig = px.pie(
        df_types,
        values='Liczba',
        names='Typ',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Client wealth distribution
    st.write("**Rozkład oceny zamożności klientów**")
    
    # Generate sample data
    wealth_data = {
        'Ocena': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Liczba klientów': [5, 8, 12, 15, 20, 18, 10, 7, 3, 2]
    }
    
    df_wealth = pd.DataFrame(wealth_data)
    
    fig = px.bar(
        df_wealth,
        x='Ocena',
        y='Liczba klientów',
        color='Liczba klientów',
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Client acquisition over time
    st.write("**Pozyskiwanie klientów w czasie**")
    
    # Generate sample data
    months = ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj', 'Cze', 'Lip', 'Sie', 'Wrz', 'Paź', 'Lis', 'Gru']
    acquisition_data = {
        'Miesiąc': months,
        'Liczba nowych klientów': [3, 5, 7, 8, 10, 12, 15, 13, 11, 9, 7, 5]
    }
    
    df_acquisition = pd.DataFrame(acquisition_data)
    
    fig = px.line(
        df_acquisition,
        x='Miesiąc',
        y='Liczba nowych klientów',
        markers=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Client communication analysis
    st.write("**Analiza komunikacji z klientami**")
    
    # Generate sample data
    communication_data = {
        'Kanał': ['Email', 'Telefon', 'SMS', 'Osobisty'],
        'Liczba': [45, 30, 15, 10]
    }
    
    df_communication = pd.DataFrame(communication_data)
    
    fig = px.bar(
        df_communication,
        x='Kanał',
        y='Liczba',
        color='Kanał'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Client satisfaction
    st.write("**Satysfakcja klientów**")
    
    # Generate sample data
    satisfaction_data = {
        'Ocena': ['1 (Niezadowolony)', '2', '3', '4', '5 (Bardzo zadowolony)'],
        'Procent': [5, 10, 20, 35, 30]
    }
    
    df_satisfaction = pd.DataFrame(satisfaction_data)
    
    fig = px.pie(
        df_satisfaction,
        values='Procent',
        names='Ocena',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
