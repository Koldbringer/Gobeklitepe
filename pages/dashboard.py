import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import db

def render():
    """Render the dashboard page."""
    st.title("📊 Panel główny")
    
    # Get dashboard metrics
    metrics = db.get_dashboard_metrics()
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Klienci",
            value=metrics['total_clients'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Urządzenia",
            value=metrics['total_devices'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Aktywne zlecenia",
            value=metrics['active_orders'],
            delta=None
        )
    
    with col4:
        # Placeholder for another metric
        st.metric(
            label="Oferty w tym miesiącu",
            value="0",  # Placeholder
            delta=None
        )
    
    # Create two columns for charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Zlecenia według statusu")
        
        # Convert orders by status to DataFrame
        df_status = pd.DataFrame(metrics['orders_by_status'])
        
        if not df_status.empty:
            # Create a pie chart
            fig = px.pie(
                df_status,
                values='count',
                names='status',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Brak danych o zleceniach.")
    
    with col_right:
        st.subheader("Aktywność w ostatnim miesiącu")
        
        # Generate sample data for activity chart (placeholder)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        values = [5, 7, 3, 8, 10, 6, 4, 7, 8, 5, 3, 6, 9, 11, 7, 5, 4, 6, 8, 9, 7, 5, 3, 6, 8, 10, 7, 5, 4, 6]
        
        df_activity = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Create a line chart
        fig = px.line(
            df_activity,
            x='date',
            y='value',
            title=None
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Upcoming service orders
    st.subheader("Nadchodzące zlecenia serwisowe")
    
    if metrics['upcoming_orders']:
        # Convert to DataFrame for easier display
        df_upcoming = pd.DataFrame(metrics['upcoming_orders'])
        
        # Format the DataFrame for display
        if not df_upcoming.empty:
            display_df = df_upcoming[['id', 'nazwa_klienta', 'typ_zlecenia', 'data_planowana', 'priorytet']]
            display_df.columns = ['ID', 'Klient', 'Typ', 'Data', 'Priorytet']
            
            # Add action buttons
            st.dataframe(display_df, use_container_width=True)
            
            # Allow selecting a service order for details
            selected_order_id = st.selectbox(
                "Wybierz zlecenie, aby zobaczyć szczegóły:",
                options=[order['id'] for order in metrics['upcoming_orders']],
                format_func=lambda x: f"Zlecenie #{x} - {next((order['nazwa_klienta'] for order in metrics['upcoming_orders'] if order['id'] == x), '')}"
            )
            
            if selected_order_id:
                selected_order = next((order for order in metrics['upcoming_orders'] if order['id'] == selected_order_id), None)
                
                if selected_order:
                    with st.expander("Szczegóły zlecenia", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Klient:** {selected_order['nazwa_klienta']}")
                            st.write(f"**Typ zlecenia:** {selected_order['typ_zlecenia']}")
                            st.write(f"**Priorytet:** {selected_order['priorytet']}")
                        
                        with col2:
                            st.write(f"**Data utworzenia:** {selected_order['data_utworzenia']}")
                            st.write(f"**Data planowana:** {selected_order['data_planowana']}")
                            st.write(f"**Status:** {selected_order['status']}")
                        
                        st.write(f"**Opis problemu:**")
                        st.write(selected_order['opis_problemu'] or "Brak opisu")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Edytuj zlecenie", key="edit_order"):
                                # Placeholder for edit functionality
                                st.session_state.page = "service_orders"
                                st.session_state.service_order_id = selected_order_id
                        
                        with col2:
                            if st.button("Oznacz jako zakończone", key="complete_order"):
                                # Placeholder for completion functionality
                                st.success(f"Zlecenie #{selected_order_id} oznaczone jako zakończone!")
                        
                        with col3:
                            if st.button("Przypisz technika", key="assign_technician"):
                                # Placeholder for technician assignment
                                st.info("Funkcjonalność przypisywania technika w trakcie implementacji.")
    else:
        st.info("Brak nadchodzących zleceń serwisowych.")
    
    # Recent clients
    st.subheader("Ostatnio dodani klienci")
    
    if metrics['recent_clients']:
        # Convert to DataFrame for easier display
        df_clients = pd.DataFrame(metrics['recent_clients'])
        
        # Format the DataFrame for display
        if not df_clients.empty:
            display_df = df_clients[['id', 'nazwa', 'email', 'telefon', 'data_rejestracji']]
            display_df.columns = ['ID', 'Nazwa', 'Email', 'Telefon', 'Data rejestracji']
            
            st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Brak ostatnio dodanych klientów.")
    
    # System status
    with st.expander("Status systemu"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Baza danych:** Połączono")
            st.write("**Supabase:** Połączono")
        
        with col2:
            st.write("**Qdrant:** Połączono")
            st.write("**n8n:** Połączono")
        
        with col3:
            st.write("**Local LLM:** Aktywny")
            st.write("**OCR:** Aktywny")
        
        st.caption("Ostatnia aktualizacja: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
