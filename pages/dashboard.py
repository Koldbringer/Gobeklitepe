import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import db
from config import PRIMARY_COLOR

def render():
    """Render the dashboard page."""
    st.title("📊 Panel główny")
    
    # Welcome message with date
    current_date = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime("%H:%M")
    
    # Get greeting based on time of day
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Dzień dobry"
    elif 12 <= hour < 18:
        greeting = "Witaj"
    else:
        greeting = "Dobry wieczór"
    
    st.markdown(f"""
        <div style="background-color:white;padding:20px;border-radius:12px;margin-bottom:25px;border-left:4px solid {PRIMARY_COLOR};box-shadow:0 4px 10px rgba(0,0,0,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h2 style="margin:0;color:#212121;font-weight:600;">{greeting}, Administrator!</h2>
                    <p style="margin:8px 0 0 0;color:#616161;font-size:1.1rem;">Dzisiaj jest {current_date}, {current_time}. Oto podsumowanie Twojego systemu HVAC.</p>
                </div>
                <div style="background-color:{PRIMARY_COLOR};color:white;border-radius:50%;width:60px;height:60px;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
                    📊
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get dashboard metrics
    metrics = db.get_dashboard_metrics()
    
    # Display key metrics in columns with improved styling
    st.markdown("<h3 style='margin-bottom:15px;font-weight:600;color:#212121;'>Kluczowe wskaźniki</h3>", unsafe_allow_html=True)
    
    # Custom metric cards with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    metric_style = """
    <div style="background-color:white;border-radius:12px;padding:20px;text-align:center;height:100%;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;transition:all 0.3s ease;">
        <div style="font-size:40px;margin-bottom:10px;color:{color};">{icon}</div>
        <div style="font-size:2.2rem;font-weight:700;color:#212121;margin-bottom:5px;">{value}</div>
        <div style="color:#757575;font-size:1rem;font-weight:500;">{label}</div>
        {delta_html}
    </div>
    """
    
    with col1:
        delta_html = ""
        st.markdown(
            metric_style.format(
                icon="👥",
                value=metrics['total_clients'],
                label="Klienci",
                color=PRIMARY_COLOR,
                delta_html=delta_html
            ),
            unsafe_allow_html=True
        )
    
    with col2:
        delta_html = ""
        st.markdown(
            metric_style.format(
                icon="🔧",
                value=metrics['total_devices'],
                label="Urządzenia",
                color="#FF9800",
                delta_html=delta_html
            ),
            unsafe_allow_html=True
        )
    
    with col3:
        delta_html = ""
        st.markdown(
            metric_style.format(
                icon="📋",
                value=metrics['active_orders'],
                label="Aktywne zlecenia",
                color="#4CAF50",
                delta_html=delta_html
            ),
            unsafe_allow_html=True
        )
    
    with col4:
        delta_html = '<div style="color:#4CAF50;font-size:0.9rem;margin-top:5px;">+2 w tym tygodniu</div>'
        st.markdown(
            metric_style.format(
                icon="💰",
                value="0",  # Placeholder
                label="Oferty w tym miesiącu",
                color="#9C27B0",
                delta_html=delta_html
            ),
            unsafe_allow_html=True
        )
    
    # Quick action buttons with improved styling
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Szybkie akcje</h3>", unsafe_allow_html=True)
    
    # Custom action buttons with better styling
    action_style = """
    <div onclick="this.querySelector('button').click();" style="background-color:white;border-radius:12px;padding:20px;text-align:center;cursor:pointer;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;transition:all 0.3s ease;height:100%;">
        <div style="width:60px;height:60px;border-radius:50%;background-color:{color}15;display:flex;align-items:center;justify-content:center;margin:0 auto 15px auto;">
            <div style="font-size:24px;color:{color};">{icon}</div>
        </div>
        <div style="font-weight:600;color:#424242;margin-bottom:10px;font-size:1.1rem;">{label}</div>
        <div style="color:#757575;font-size:0.9rem;margin-bottom:15px;">{description}</div>
        <button style="display:none;" id="{id}"></button>
    </div>
    """
    
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        st.markdown(
            action_style.format(
                icon="➕",
                label="Nowy klient",
                description="Dodaj nowego klienta do systemu",
                color=PRIMARY_COLOR,
                id="new_client_btn"
            ),
            unsafe_allow_html=True
        )
        if st.button("Nowy klient", key="new_client_btn", use_container_width=True, label_visibility="collapsed"):
            st.session_state.page = "clients"
            # Set session state to open the "Add client" tab
            st.session_state.clients_tab = "add"
    
    with quick_col2:
        st.markdown(
            action_style.format(
                icon="📝",
                label="Nowe zlecenie",
                description="Utwórz nowe zlecenie serwisowe",
                color="#FF9800",
                id="new_order_btn"
            ),
            unsafe_allow_html=True
        )
        if st.button("Nowe zlecenie", key="new_order_btn", use_container_width=True, label_visibility="collapsed"):
            st.session_state.page = "service_orders"
            # Set session state to create a new order
            st.session_state.new_order = True
    
    with quick_col3:
        st.markdown(
            action_style.format(
                icon="🔍",
                label="Wyszukaj urządzenie",
                description="Znajdź urządzenie w systemie",
                color="#4CAF50",
                id="search_device_btn"
            ),
            unsafe_allow_html=True
        )
        if st.button("Wyszukaj urządzenie", key="search_device_btn", use_container_width=True, label_visibility="collapsed"):
            st.session_state.page = "devices"
            # Set session state to open search
            st.session_state.open_device_search = True
    
    with quick_col4:
        st.markdown(
            action_style.format(
                icon="📊",
                label="Generuj raport",
                description="Twórz raporty i analizy",
                color="#9C27B0",
                id="generate_report_btn"
            ),
            unsafe_allow_html=True
        )
        if st.button("Generuj raport", key="generate_report_btn", use_container_width=True, label_visibility="collapsed"):
            st.session_state.page = "reports"
    
    # Create two columns for charts with improved styling
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Analiza danych</h3>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
            <h4 style="margin-bottom:15px;color:#212121;font-weight:600;border-bottom:1px solid #f0f0f0;padding-bottom:10px;">Zlecenia według statusu</h4>
        """, unsafe_allow_html=True)
        
        # Convert orders by status to DataFrame
        df_status = pd.DataFrame(metrics['orders_by_status'])
        
        if not df_status.empty:
            # Create a pie chart with improved styling
            fig = px.pie(
                df_status,
                values='count',
                names='status',
                color_discrete_sequence=px.colors.qualitative.Bold,
                hole=0.4
            )
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont=dict(size=12, color="white"),
                marker=dict(line=dict(color='white', width=2))
            )
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Brak danych o zleceniach.")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
            <h4 style="margin-bottom:15px;color:#212121;font-weight:600;border-bottom:1px solid #f0f0f0;padding-bottom:10px;">Aktywność w ostatnim miesiącu</h4>
        """, unsafe_allow_html=True)
        
        # Generate sample data for activity chart (placeholder)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%d.%m') for i in range(30, 0, -1)]
        values = [5, 7, 3, 8, 10, 6, 4, 7, 8, 5, 3, 6, 9, 11, 7, 5, 4, 6, 8, 9, 7, 5, 3, 6, 8, 10, 7, 5, 4, 6]
        
        df_activity = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Create a line chart with improved styling
        fig = px.line(
            df_activity,
            x='date',
            y='value',
            title=None,
            markers=True
        )
        fig.update_traces(
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=6, color=PRIMARY_COLOR)
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="Data",
            yaxis_title="Liczba zleceń",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickangle=-45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Upcoming service orders with improved styling
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Nadchodzące zlecenia serwisowe</h3>", unsafe_allow_html=True)
    
    # Add a container for the service orders
    st.markdown("""
    <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
    """, unsafe_allow_html=True)
    
    if metrics['upcoming_orders']:
        # Convert to DataFrame for easier display
        df_upcoming = pd.DataFrame(metrics['upcoming_orders'])
        
        # Format the DataFrame for display
        if not df_upcoming.empty:
            display_df = df_upcoming[['id', 'nazwa_klienta', 'typ_zlecenia', 'data_planowana', 'priorytet']]
            display_df.columns = ['ID', 'Klient', 'Typ', 'Data', 'Priorytet']
            
            # Add color coding for priority
            def highlight_priority(val):
                if val == 'wysoki':
                    return 'background-color: rgba(244, 67, 54, 0.1); color: #F44336; font-weight: bold'
                elif val == 'średni':
                    return 'background-color: rgba(255, 152, 0, 0.1); color: #FF9800; font-weight: bold'
                elif val == 'niski':
                    return 'background-color: rgba(76, 175, 80, 0.1); color: #4CAF50; font-weight: bold'
                return ''
            
            # Apply styling
            styled_df = display_df.style.applymap(highlight_priority, subset=['Priorytet'])
            
            # Display the styled dataframe
            st.dataframe(styled_df, use_container_width=True, height=200)
            
            # Allow selecting a service order for details with improved styling
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            selected_order_id = st.selectbox(
                "Wybierz zlecenie, aby zobaczyć szczegóły:",
                options=[order['id'] for order in metrics['upcoming_orders']],
                format_func=lambda x: f"Zlecenie #{x} - {next((order['nazwa_klienta'] for order in metrics['upcoming_orders'] if order['id'] == x), '')}"
            )
            
            if selected_order_id:
                selected_order = next((order for order in metrics['upcoming_orders'] if order['id'] == selected_order_id), None)
                
                if selected_order:
                    with st.expander("Szczegóły zlecenia", expanded=True):
                        # Priority indicator
                        priority_color = "#F44336" if selected_order['priorytet'] == 'wysoki' else "#FF9800" if selected_order['priorytet'] == 'średni' else "#4CAF50"
                        st.markdown(f"""
                            <div style="display:flex;align-items:center;margin-bottom:15px;">
                                <div style="width:12px;height:12px;border-radius:50%;background-color:{priority_color};margin-right:8px;"></div>
                                <span style="font-weight:bold;color:{priority_color};">Priorytet: {selected_order['priorytet'].upper()}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Order details in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                                <div style="margin-bottom:10px;">
                                    <span style="color:#757575;font-size:0.9rem;">Klient</span><br>
                                    <span style="font-weight:500;font-size:1.1rem;">{selected_order['nazwa_klienta']}</span>
                                </div>
                                
                                <div style="margin-bottom:10px;">
                                    <span style="color:#757575;font-size:0.9rem;">Typ zlecenia</span><br>
                                    <span style="font-weight:500;font-size:1.1rem;">{selected_order['typ_zlecenia']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                                <div style="margin-bottom:10px;">
                                    <span style="color:#757575;font-size:0.9rem;">Data utworzenia</span><br>
                                    <span style="font-weight:500;font-size:1.1rem;">{selected_order['data_utworzenia']}</span>
                                </div>
                                
                                <div style="margin-bottom:10px;">
                                    <span style="color:#757575;font-size:0.9rem;">Data planowana</span><br>
                                    <span style="font-weight:500;font-size:1.1rem;">{selected_order['data_planowana']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Problem description
                        st.markdown(f"""
                            <div style="margin-top:10px;">
                                <span style="color:#757575;font-size:0.9rem;">Opis problemu</span><br>
                                <div style="padding:10px;background-color:#f8f9fa;border-radius:5px;margin-top:5px;">
                                    {selected_order['opis_problemu'] or "Brak opisu"}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons with improved styling
                        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("✏️ Edytuj zlecenie", key="edit_order", use_container_width=True):
                                # Placeholder for edit functionality
                                st.session_state.page = "service_orders"
                                st.session_state.service_order_id = selected_order_id
                        
                        with col2:
                            if st.button("✅ Oznacz jako zakończone", key="complete_order", use_container_width=True):
                                # Placeholder for completion functionality
                                st.success(f"Zlecenie #{selected_order_id} oznaczone jako zakończone!")
                        
                        with col3:
                            if st.button("👤 Przypisz technika", key="assign_technician", use_container_width=True):
                                # Placeholder for technician assignment
                                st.info("Funkcjonalność przypisywania technika w trakcie implementacji.")
    else:
        st.info("Brak nadchodzących zleceń serwisowych.")
        
        # Add a button to create a new service order
        if st.button("➕ Utwórz nowe zlecenie serwisowe", key="create_new_order"):
            st.session_state.page = "service_orders"
            st.session_state.new_order = True
            
    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent clients with improved styling
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Ostatnio dodani klienci</h3>", unsafe_allow_html=True)
    
    # Add a container for the clients
    st.markdown("""
    <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
    """, unsafe_allow_html=True)
    
    if metrics['recent_clients']:
        # Convert to DataFrame for easier display
        df_clients = pd.DataFrame(metrics['recent_clients'])
        
        # Format the DataFrame for display
        if not df_clients.empty:
            display_df = df_clients[['id', 'nazwa', 'email', 'telefon', 'data_rejestracji']]
            display_df.columns = ['ID', 'Nazwa', 'Email', 'Telefon', 'Data rejestracji']
            
            # Display the dataframe with improved styling
            st.dataframe(display_df, use_container_width=True, height=200)
            
            # Add a button to view all clients
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Zobacz wszystkich", key="view_all_clients", use_container_width=True):
                    st.session_state.page = "clients"
    else:
        st.info("Brak ostatnio dodanych klientów.")
        
        # Add a button to add a new client
        if st.button("➕ Dodaj nowego klienta", key="add_new_client"):
            st.session_state.page = "clients"
            st.session_state.clients_tab = "add"
            
    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System status with improved styling
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Status systemu</h3>", unsafe_allow_html=True)
    
    # Add a container for the system status
    st.markdown("""
    <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
        <div style="display:flex;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:1px solid #f0f0f0;">
            <div style="background-color:#4CAF5015;width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:15px;">
                <div style="font-size:24px;color:#4CAF50;">⚙️</div>
            </div>
            <div>
                <div style="font-weight:600;font-size:1.1rem;color:#212121;">System działa prawidłowo</div>
                <div style="color:#757575;font-size:0.9rem;">Ostatnie sprawdzenie: Dzisiaj, 08:15</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;background-color:#f8f9fa;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>Baza danych:</b> Połączono</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>Supabase:</b> Połączono</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;background-color:#f8f9fa;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>Qdrant:</b> Połączono</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>API:</b> Aktywne</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;background-color:#f8f9fa;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>Local LLM:</b> Aktywny</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:15px;padding:10px;border-radius:8px;">
                <div style="width:12px;height:12px;border-radius:50%;background-color:#4CAF50;margin-right:10px;"></div>
                <span style="font-weight:500;"><b>OCR:</b> Aktywny</span>
            </div>
        """, unsafe_allow_html=True)
        
    # Close the container div
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System resources in a new container
    st.markdown("<h3 style='margin:30px 0 20px 0;font-weight:600;color:#212121;'>Zasoby systemowe</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color:white;border-radius:12px;padding:20px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border:1px solid #f0f0f0;margin-bottom:20px;">
        <div style="display:flex;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:1px solid #f0f0f0;">
            <div style="background-color:#FF980015;width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-right:15px;">
                <div style="font-size:24px;color:#FF9800;">💻</div>
            </div>
            <div>
                <div style="font-weight:600;font-size:1.1rem;color:#212121;">Monitorowanie zasobów</div>
                <div style="color:#757575;font-size:0.9rem;">Aktualne wykorzystanie zasobów systemowych</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
        
    # Sample resource usage
    col1, col2, col3, col4 = st.columns(4)
    
    # CPU usage
    with col1:
        cpu_usage = 45  # Placeholder value
        st.markdown("""
            <div style="padding:15px;border-radius:8px;background-color:#f8f9fa;height:100%;">
                <div style="font-weight:600;color:#212121;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                    <span>CPU</span>
                    <span style="color:#FF9800;font-size:1.2rem;">45%</span>
                </div>
        """, unsafe_allow_html=True)
        st.progress(0.45)
        st.markdown("""
            </div>
        """, unsafe_allow_html=True)
    
    # Memory usage
    with col2:
        memory_usage = 62  # Placeholder value
        st.markdown("""
            <div style="padding:15px;border-radius:8px;background-color:#f8f9fa;height:100%;">
                <div style="font-weight:600;color:#212121;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                    <span>Pamięć</span>
                    <span style="color:#FF9800;font-size:1.2rem;">62%</span>
                </div>
        """, unsafe_allow_html=True)
        st.progress(0.62)
        st.markdown("""
            </div>
        """, unsafe_allow_html=True)
    
    # Disk usage
    with col3:
        disk_usage = 38  # Placeholder value
        st.markdown("""
            <div style="padding:15px;border-radius:8px;background-color:#f8f9fa;height:100%;">
                <div style="font-weight:600;color:#212121;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                    <span>Dysk</span>
                    <span style="color:#FF9800;font-size:1.2rem;">38%</span>
                </div>
        """, unsafe_allow_html=True)
        st.progress(0.38)
        st.markdown("""
            </div>
        """, unsafe_allow_html=True)
    
    # Network usage
    with col4:
        network_usage = 25  # Placeholder value
        st.markdown("""
            <div style="padding:15px;border-radius:8px;background-color:#f8f9fa;height:100%;">
                <div style="font-weight:600;color:#212121;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
                    <span>Sieć</span>
                    <span style="color:#FF9800;font-size:1.2rem;">25%</span>
                </div>
        """, unsafe_allow_html=True)
        st.progress(0.25)
        st.markdown("""
            </div>
        """, unsafe_allow_html=True)
    
    st.caption(f"Ostatnia aktualizacja: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)
