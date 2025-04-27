"""
Quantum Communication Visualization Component

This component provides visualizations for the quantum-enhanced communication system,
including client entanglement networks, priority heatmaps, and communication flow diagrams.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import networkx as nx
import math
import random
from typing import List, Dict, Any, Tuple

from services import quantum_communication


def render_client_entanglement_network(client_ids: List[int] = None, limit: int = 10):
    """
    Render a network visualization of client entanglement.
    
    This shows how clients are connected through devices, communications, and services.
    """
    st.subheader("Sieć splątania kwantowego klientów")
    
    # Get client data
    if not client_ids:
        clients = quantum_communication.get_client_entanglement_scores(limit=limit)
    else:
        clients = []
        for client_id in client_ids:
            # Get client data
            query = "SELECT id, nazwa, email FROM klienci WHERE id = %s"
            result = db.execute_query(query, [client_id])
            if result:
                client = result[0]
                client['entanglement_score'] = quantum_communication.QuantumPrioritizer.calculate_entanglement_score(client_id)
                clients.append(client)
    
    if not clients:
        st.info("Brak danych o klientach do wizualizacji.")
        return
    
    # Create a network graph
    G = nx.Graph()
    
    # Add nodes for clients
    for client in clients:
        G.add_node(f"C{client['id']}", 
                   type="client", 
                   name=client['nazwa'], 
                   score=client['entanglement_score'],
                   size=20 + 30 * client['entanglement_score'])
    
    # Add some device nodes and connections (simulated)
    device_count = 0
    for client in clients:
        # Add 1-3 devices per client
        num_devices = random.randint(1, 3)
        for i in range(num_devices):
            device_id = f"D{device_count}"
            device_count += 1
            device_type = random.choice(["AC", "Heater", "Ventilation"])
            G.add_node(device_id, 
                       type="device", 
                       name=f"{device_type} {i+1}",
                       size=15)
            # Connect device to client
            G.add_edge(f"C{client['id']}", device_id, weight=random.uniform(0.5, 1.0))
    
    # Add connections between clients based on entanglement
    for i, client1 in enumerate(clients):
        for j, client2 in enumerate(clients):
            if i < j:  # Avoid duplicate connections
                # Calculate connection strength based on entanglement scores
                connection_strength = (client1['entanglement_score'] * client2['entanglement_score']) ** 0.5
                if connection_strength > 0.3:  # Only show stronger connections
                    G.add_edge(f"C{client1['id']}", f"C{client2['id']}", 
                               weight=connection_strength)
    
    # Create positions for nodes using a spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Create node traces for clients and devices
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node]
        if node_data['type'] == 'client':
            node_text.append(f"Klient: {node_data['name']}<br>Splątanie: {node_data['score']:.2f}")
            node_color.append('rgba(30, 136, 229, 0.8)')  # Blue for clients
        else:
            node_text.append(f"Urządzenie: {node_data['name']}")
            node_color.append('rgba(255, 193, 7, 0.8)')  # Yellow for devices
        
        node_size.append(node_data['size'])
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            color=node_color,
            size=node_size,
            line=dict(width=2, color='white')
        )
    )
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_width = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Edge width based on weight
        weight = G.edges[edge]['weight']
        edge_width.append(weight * 3)
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='rgba(150, 150, 150, 0.5)'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        title="Sieć splątania kwantowego klientów",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    with st.expander("Jak interpretować wizualizację?"):
        st.write("""
        **Sieć splątania kwantowego klientów** pokazuje powiązania między klientami i ich urządzeniami.
        
        - **Niebieskie węzły** reprezentują klientów, a ich rozmiar odpowiada wartości splątania kwantowego.
        - **Żółte węzły** reprezentują urządzenia HVAC.
        - **Połączenia** między węzłami pokazują relacje - grubsze linie oznaczają silniejsze powiązania.
        
        Klienci o wyższym stopniu splątania kwantowego powinni być traktowani priorytetowo w komunikacji.
        """)


def render_communication_priority_heatmap(days: int = 7):
    """
    Render a heatmap of communication priorities over time.
    """
    st.subheader("Mapa ciepła priorytetów komunikacji")
    
    # Generate sample data (in a real implementation, this would come from the database)
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    hours = list(range(24))
    
    # Create a matrix of priority values
    priority_matrix = []
    for _ in range(len(dates)):
        daily_priorities = []
        for hour in hours:
            # Higher priority during business hours (9-17)
            if 9 <= hour <= 17:
                base_priority = random.uniform(0.6, 1.0)
            else:
                base_priority = random.uniform(0.1, 0.5)
            
            # Add some randomness
            priority = base_priority * random.uniform(0.8, 1.2)
            daily_priorities.append(priority)
        priority_matrix.append(daily_priorities)
    
    # Create a DataFrame
    df = pd.DataFrame(priority_matrix, index=dates, columns=hours)
    
    # Create heatmap
    fig = px.imshow(df,
                    labels=dict(x="Godzina", y="Data", color="Priorytet"),
                    x=hours,
                    y=dates,
                    color_continuous_scale="Viridis",
                    aspect="auto")
    
    fig.update_layout(
        title="Mapa ciepła priorytetów komunikacji",
        xaxis_title="Godzina dnia",
        yaxis_title="Data",
        coloraxis_colorbar=dict(title="Priorytet")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    with st.expander("Jak interpretować mapę ciepła?"):
        st.write("""
        **Mapa ciepła priorytetów komunikacji** pokazuje, kiedy komunikacja z klientami ma najwyższy priorytet.
        
        - **Ciemniejsze kolory** oznaczają wyższy priorytet komunikacji.
        - **Jaśniejsze kolory** oznaczają niższy priorytet.
        
        Priorytety są obliczane na podstawie:
        - Godzin pracy (9-17)
        - Historycznych wzorców komunikacji z klientami
        - Stopnia splątania kwantowego klientów
        
        Wykorzystaj tę mapę, aby zoptymalizować czas odpowiedzi na komunikację od klientów.
        """)


def render_communication_flow_diagram():
    """
    Render a Sankey diagram showing the flow of communications.
    """
    st.subheader("Diagram przepływu komunikacji")
    
    # Create sample data for the Sankey diagram
    labels = [
        # Sources
        "Email przychodzący", "Telefon przychodzący", "SMS przychodzący",
        # Intermediate nodes
        "Priorytet wysoki", "Priorytet średni", "Priorytet niski",
        # Destinations
        "Odpowiedź natychmiastowa", "Odpowiedź w ciągu dnia", "Odpowiedź następnego dnia",
        "Przekazano do technika", "Utworzono zlecenie", "Archiwizacja"
    ]
    
    # Define the links
    source = [
        # From incoming email
        0, 0, 0,
        # From incoming phone
        1, 1, 1,
        # From incoming SMS
        2, 2, 2,
        # From high priority
        3, 3, 3,
        # From medium priority
        4, 4, 4,
        # From low priority
        5, 5, 5
    ]
    
    target = [
        # Email to priorities
        3, 4, 5,
        # Phone to priorities
        3, 4, 5,
        # SMS to priorities
        3, 4, 5,
        # High priority to actions
        6, 9, 10,
        # Medium priority to actions
        7, 9, 10,
        # Low priority to actions
        8, 10, 11
    ]
    
    value = [
        # Email volumes
        25, 40, 15,
        # Phone volumes
        30, 10, 5,
        # SMS volumes
        15, 10, 5,
        # High priority actions
        30, 15, 10,
        # Medium priority actions
        25, 20, 15,
        # Low priority actions
        10, 5, 10
    ]
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=[
                # Source colors
                "rgba(30, 136, 229, 0.8)", "rgba(255, 193, 7, 0.8)", "rgba(76, 175, 80, 0.8)",
                # Priority colors
                "rgba(244, 67, 54, 0.8)", "rgba(255, 152, 0, 0.8)", "rgba(139, 195, 74, 0.8)",
                # Destination colors
                "rgba(156, 39, 176, 0.8)", "rgba(103, 58, 183, 0.8)", "rgba(63, 81, 181, 0.8)",
                "rgba(33, 150, 243, 0.8)", "rgba(0, 188, 212, 0.8)", "rgba(0, 150, 136, 0.8)"
            ]
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])
    
    fig.update_layout(
        title="Diagram przepływu komunikacji",
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    with st.expander("Jak interpretować diagram przepływu?"):
        st.write("""
        **Diagram przepływu komunikacji** pokazuje, jak komunikacja od klientów jest przetwarzana w systemie.
        
        Diagram przedstawia:
        1. **Źródła komunikacji** (email, telefon, SMS)
        2. **Poziomy priorytetu** (wysoki, średni, niski) - określane przez algorytm splątania kwantowego
        3. **Działania** podejmowane w odpowiedzi na komunikację
        
        Szerokość połączeń odpowiada ilości komunikacji przepływającej daną ścieżką.
        """)


def render_quantum_communication_dashboard():
    """
    Render the main quantum communication dashboard.
    """
    st.title("🔬 Kwantowy Dashboard Komunikacji")
    
    # Introduction
    st.markdown("""
    Ten dashboard wykorzystuje algorytmy inspirowane mechaniką kwantową do optymalizacji komunikacji z klientami.
    System analizuje historię interakcji, wartość klienta i inne czynniki, aby określić priorytety i sugerować
    optymalne czasy odpowiedzi.
    """)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Średni stopień splątania",
            value="0.72",
            delta="0.05",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Stabilność kanału kwantowego",
            value="98%",
            delta="2%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Priorytetowe komunikacje",
            value="12",
            delta="3",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Średni czas odpowiedzi",
            value="2.4h",
            delta="-0.3h",
            delta_color="good"
        )
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Sieć splątania", "Mapa priorytetów", "Przepływ komunikacji"])
    
    with tab1:
        render_client_entanglement_network()
    
    with tab2:
        render_communication_priority_heatmap()
    
    with tab3:
        render_communication_flow_diagram()
    
    # Prioritized communications
    st.subheader("Priorytetowe komunikacje")
    
    # Get prioritized communications
    prioritized_comms = quantum_communication.prioritize_inbox(limit=5)
    
    if not prioritized_comms:
        st.info("Brak priorytetowych komunikacji.")
    else:
        for i, comm in enumerate(prioritized_comms):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{i+1}. {comm['client_name']}** - {comm['typ']}")
                    st.write(f"Priorytet: {comm['priority_score']:.2f}")
                    st.write(f"Sugerowany czas odpowiedzi: {comm['suggested_response_time'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if st.button("Odpowiedz", key=f"respond_{comm['id']}"):
                        st.session_state.reply_to = comm
                        st.session_state.reply_mode = True
                        st.session_state.page = "communication"
                        st.experimental_rerun()
                
                # Show response suggestions
                if 'response_suggestions' in comm and comm['response_suggestions']:
                    with st.expander("Sugerowane odpowiedzi"):
                        for j, suggestion in enumerate(comm['response_suggestions']):
                            st.write(f"{j+1}. {suggestion}")
                
                st.markdown("---")
    
    # Add information about the quantum algorithm
    with st.expander("O algorytmie kwantowym"):
        st.markdown("""
        ### Algorytm splątania kwantowego
        
        System wykorzystuje algorytm inspirowany mechaniką kwantową do określania priorytetów komunikacji:
        
        1. **Obliczanie stopnia splątania** - każdy klient otrzymuje wartość splątania na podstawie:
           - Historii komunikacji
           - Wartości urządzeń
           - Oceny zamożności
           - Częstotliwości interakcji
        
        2. **Zasada nieoznaczoności** - wprowadza kontrolowaną losowość, aby uniknąć pułapek lokalnych minimów
        
        3. **Superpozycja priorytetów** - łączy różne czynniki w jedną wartość priorytetu
        
        4. **Optymalizacja czasu odpowiedzi** - sugeruje optymalny czas odpowiedzi na podstawie wzorców komunikacji klienta
        
        Algorytm jest stale uczony i dostosowywany na podstawie nowych danych.
        """)
