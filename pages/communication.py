import streamlit as st
import pandas as pd
import io
from datetime import datetime
import logging
from services import communication_service
from utils import db

logger = logging.getLogger(__name__)

def render():
    """Render the communication page."""
    st.title("✉️ Komunikacja")
    
    # Create tabs for different communication features
    tab1, tab2, tab3, tab4 = st.tabs(["Skrzynka odbiorcza", "Wyślij wiadomość", "Historia komunikacji", "Szablony"])
    
    with tab1:
        render_inbox()
    
    with tab2:
        render_send_message()
    
    with tab3:
        render_communication_history()
    
    with tab4:
        render_templates()


def render_inbox():
    """Render the inbox tab."""
    st.subheader("Skrzynka odbiorcza")
    
    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Odśwież", key="refresh_inbox"):
            with st.spinner("Pobieranie nowych wiadomości..."):
                result = communication_service.process_incoming_communications()
                st.success(f"Pobrano {result['emails']} nowych wiadomości")
                st.experimental_rerun()
    
    # Get recent communications
    communications = get_recent_communications(comm_type="email", direction="przychodzący", limit=10)
    
    if not communications:
        st.info("Brak nowych wiadomości w skrzynce odbiorczej.")
        return
    
    # Display communications
    for comm in communications:
        with st.expander(f"{comm['subject']} - {comm['from_name']} ({comm['data_czas'].strftime('%d.%m.%Y %H:%M')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Od:** {comm['from_name']} ({comm['from_email']})")
                st.write(f"**Data:** {comm['data_czas'].strftime('%d.%m.%Y %H:%M')}")
                st.write(f"**Temat:** {comm['subject']}")
                
                if comm['kategoria']:
                    st.write(f"**Kategoria:** {comm['kategoria']}")
                
                if comm['klasyfikacja']:
                    st.write(f"**Klasyfikacja:** {comm['klasyfikacja']}")
                
                if comm['analiza_sentymentu'] is not None:
                    sentiment = comm['analiza_sentymentu']
                    sentiment_text = "Pozytywny" if sentiment > 0.2 else "Neutralny" if sentiment > -0.2 else "Negatywny"
                    st.write(f"**Sentyment:** {sentiment_text} ({sentiment:.2f})")
            
            with col2:
                st.write("**Akcje:**")
                if st.button("Odpowiedz", key=f"reply_{comm['id']}"):
                    st.session_state.reply_to = comm
                    st.session_state.reply_mode = True
                
                if st.button("Oznacz jako przeczytane", key=f"mark_read_{comm['id']}"):
                    communication_service.CommunicationManager.update_communication_status(comm['id'], "przeczytane")
                    st.success("Oznaczono jako przeczytane")
                    st.experimental_rerun()
                
                if st.button("Archiwizuj", key=f"archive_{comm['id']}"):
                    communication_service.CommunicationManager.update_communication_status(comm['id'], "zarchiwizowane")
                    st.success("Wiadomość zarchiwizowana")
                    st.experimental_rerun()
            
            st.markdown("---")
            st.write("**Treść wiadomości:**")
            st.write(comm['treść'])


def render_send_message():
    """Render the send message tab."""
    st.subheader("Wyślij wiadomość")
    
    # Check if we're in reply mode
    if hasattr(st.session_state, 'reply_mode') and st.session_state.reply_mode:
        reply_to = st.session_state.reply_to
        st.info(f"Odpowiadasz na wiadomość od: {reply_to['from_name']} ({reply_to['from_email']})")
        
        if st.button("Anuluj odpowiedź"):
            st.session_state.reply_mode = False
            st.session_state.reply_to = None
            st.experimental_rerun()
    
    # Get clients for dropdown
    clients = get_clients()
    
    if not clients:
        st.warning("Brak klientów w bazie danych. Dodaj klienta, aby wysłać wiadomość.")
        return
    
    # Client selection
    selected_client_id = st.selectbox(
        "Wybierz klienta:",
        options=[client['id'] for client in clients],
        format_func=lambda x: next((f"{client['nazwa']} ({client['email']})" for client in clients if client['id'] == x), "")
    )
    
    # Get selected client details
    selected_client = next((client for client in clients if client['id'] == selected_client_id), None)
    
    if not selected_client:
        st.warning("Wybierz klienta z listy.")
        return
    
    # Message form
    with st.form("email_form"):
        # If in reply mode, pre-fill subject
        default_subject = ""
        if hasattr(st.session_state, 'reply_mode') and st.session_state.reply_mode:
            reply_to = st.session_state.reply_to
            default_subject = f"Re: {reply_to['subject']}"
        
        subject = st.text_input("Temat:", value=default_subject)
        message = st.text_area("Treść wiadomości:", height=200)
        
        # File upload
        uploaded_file = st.file_uploader("Załącznik (opcjonalnie):", type=["pdf", "docx", "xlsx", "jpg", "png"])
        
        # Submit button
        submitted = st.form_submit_button("Wyślij wiadomość")
        
        if submitted:
            if not subject or not message:
                st.error("Temat i treść wiadomości są wymagane.")
                return
            
            # Prepare attachments if any
            attachments = None
            if uploaded_file is not None:
                file_content = uploaded_file.read()
                attachments = [{
                    "filename": uploaded_file.name,
                    "content": file_content,
                    "content_type": uploaded_file.type
                }]
            
            # Send email
            with st.spinner("Wysyłanie wiadomości..."):
                communication_id = communication_service.EmailManager.send_email(
                    client_id=selected_client_id,
                    subject=subject,
                    content=message,
                    to_email=selected_client['email'],
                    attachments=attachments
                )
                
                if communication_id:
                    st.success("Wiadomość została wysłana!")
                    
                    # If in reply mode, update the original message status
                    if hasattr(st.session_state, 'reply_mode') and st.session_state.reply_mode:
                        reply_to = st.session_state.reply_to
                        communication_service.CommunicationManager.update_communication_status(reply_to['id'], "odpowiedziane")
                        st.session_state.reply_mode = False
                        st.session_state.reply_to = None
                else:
                    st.error("Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.")


def render_communication_history():
    """Render the communication history tab."""
    st.subheader("Historia komunikacji")
    
    # Get clients for dropdown
    clients = get_clients()
    
    if not clients:
        st.warning("Brak klientów w bazie danych.")
        return
    
    # Client selection
    selected_client_id = st.selectbox(
        "Wybierz klienta:",
        options=[client['id'] for client in clients],
        format_func=lambda x: next((f"{client['nazwa']} ({client['email']})" for client in clients if client['id'] == x), ""),
        key="history_client_select"
    )
    
    # Communication type filter
    comm_type = st.selectbox(
        "Typ komunikacji:",
        options=["wszystkie", "email", "telefon", "SMS"],
        index=0
    )
    
    # Get communications for selected client
    communications = get_client_communications(
        client_id=selected_client_id,
        comm_type=None if comm_type == "wszystkie" else comm_type
    )
    
    if not communications:
        st.info(f"Brak historii komunikacji dla wybranego klienta{' i typu komunikacji' if comm_type != 'wszystkie' else ''}.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(communications)
    
    # Format DataFrame
    if not df.empty:
        display_df = df[['id', 'typ', 'kierunek', 'data_czas', 'status', 'kategoria']]
        display_df.columns = ['ID', 'Typ', 'Kierunek', 'Data', 'Status', 'Kategoria']
        
        # Format date
        display_df['Data'] = display_df['Data'].dt.strftime('%d.%m.%Y %H:%M')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Allow selecting a communication for details
        selected_comm_id = st.selectbox(
            "Wybierz komunikację, aby zobaczyć szczegóły:",
            options=[comm['id'] for comm in communications],
            format_func=lambda x: f"ID: {x} - {next((comm['typ'] for comm in communications if comm['id'] == x), '')} ({next((comm['data_czas'].strftime('%d.%m.%Y %H:%M') for comm in communications if comm['id'] == x), '')})"
        )
        
        # Display selected communication details
        selected_comm = next((comm for comm in communications if comm['id'] == selected_comm_id), None)
        
        if selected_comm:
            with st.expander("Szczegóły komunikacji", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {selected_comm['id']}")
                    st.write(f"**Typ:** {selected_comm['typ']}")
                    st.write(f"**Kierunek:** {selected_comm['kierunek']}")
                    st.write(f"**Data:** {selected_comm['data_czas'].strftime('%d.%m.%Y %H:%M')}")
                
                with col2:
                    st.write(f"**Status:** {selected_comm['status']}")
                    st.write(f"**Kategoria:** {selected_comm['kategoria'] or 'Brak'}")
                    
                    if selected_comm['klasyfikacja']:
                        st.write(f"**Klasyfikacja:** {selected_comm['klasyfikacja']}")
                    
                    if selected_comm['analiza_sentymentu'] is not None:
                        sentiment = selected_comm['analiza_sentymentu']
                        sentiment_text = "Pozytywny" if sentiment > 0.2 else "Neutralny" if sentiment > -0.2 else "Negatywny"
                        st.write(f"**Sentyment:** {sentiment_text} ({sentiment:.2f})")
                
                st.write("**Treść:**")
                st.write(selected_comm['treść'] or "Brak treści")
                
                if selected_comm['transkrypcja']:
                    st.write("**Transkrypcja:**")
                    st.write(selected_comm['transkrypcja'])
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if selected_comm['kierunek'] == "przychodzący" and selected_comm['typ'] == "email":
                        if st.button("Odpowiedz", key=f"history_reply_{selected_comm['id']}"):
                            # Prepare reply data
                            client = next((client for client in clients if client['id'] == selected_client_id), None)
                            reply_data = {
                                'id': selected_comm['id'],
                                'from_name': client['nazwa'],
                                'from_email': client['email'],
                                'subject': selected_comm['treść'].split('\n')[0] if selected_comm['treść'] else "Brak tematu",
                                'treść': selected_comm['treść']
                            }
                            
                            st.session_state.reply_to = reply_data
                            st.session_state.reply_mode = True
                            
                            # Switch to send message tab
                            st.session_state.active_tab = "Wyślij wiadomość"
                            st.experimental_rerun()
                
                with col2:
                    if st.button("Archiwizuj", key=f"history_archive_{selected_comm['id']}"):
                        communication_service.CommunicationManager.update_communication_status(selected_comm['id'], "zarchiwizowane")
                        st.success("Komunikacja zarchiwizowana")
                        st.experimental_rerun()
                
                with col3:
                    if st.button("Eksportuj", key=f"history_export_{selected_comm['id']}"):
                        # Export communication to CSV
                        export_data = {
                            'ID': selected_comm['id'],
                            'Typ': selected_comm['typ'],
                            'Kierunek': selected_comm['kierunek'],
                            'Data': selected_comm['data_czas'].strftime('%d.%m.%Y %H:%M'),
                            'Status': selected_comm['status'],
                            'Kategoria': selected_comm['kategoria'] or 'Brak',
                            'Klasyfikacja': selected_comm['klasyfikacja'] or 'Brak',
                            'Sentyment': selected_comm['analiza_sentymentu'] if selected_comm['analiza_sentymentu'] is not None else 'Brak',
                            'Treść': selected_comm['treść'] or 'Brak',
                            'Transkrypcja': selected_comm['transkrypcja'] or 'Brak'
                        }
                        
                        df_export = pd.DataFrame([export_data])
                        csv = df_export.to_csv(index=False)
                        
                        # Create download button
                        st.download_button(
                            label="Pobierz CSV",
                            data=csv,
                            file_name=f"komunikacja_{selected_comm['id']}.csv",
                            mime="text/csv"
                        )


def render_templates():
    """Render the templates tab."""
    st.subheader("Szablony wiadomości")
    
    # Template selection
    template_type = st.selectbox(
        "Wybierz typ szablonu:",
        options=["Powitanie", "Potwierdzenie wizyty", "Faktura", "Oferta"]
    )
    
    # Get clients for dropdown
    clients = get_clients()
    
    if not clients:
        st.warning("Brak klientów w bazie danych. Dodaj klienta, aby wysłać wiadomość z szablonu.")
        return
    
    # Client selection
    selected_client_id = st.selectbox(
        "Wybierz klienta:",
        options=[client['id'] for client in clients],
        format_func=lambda x: next((f"{client['nazwa']} ({client['email']})" for client in clients if client['id'] == x), ""),
        key="template_client_select"
    )
    
    # Get selected client details
    selected_client = next((client for client in clients if client['id'] == selected_client_id), None)
    
    if not selected_client:
        st.warning("Wybierz klienta z listy.")
        return
    
    # Template form based on selection
    if template_type == "Powitanie":
        with st.form("welcome_template_form"):
            st.write("**Szablon powitalny**")
            st.write("Ten szablon jest używany do wysyłania wiadomości powitalnej do nowego klienta.")
            
            # Preview button
            preview = st.checkbox("Podgląd szablonu")
            
            if preview:
                st.write("**Podgląd:**")
                with open("templates/email/welcome.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                    html_content = html_content.replace("{{client_name}}", selected_client['nazwa'])
                    html_content = html_content.replace("{{current_year}}", str(datetime.now().year))
                    st.components.v1.html(html_content, height=500, scrolling=True)
            
            # Submit button
            submitted = st.form_submit_button("Wyślij wiadomość powitalną")
            
            if submitted:
                with st.spinner("Wysyłanie wiadomości..."):
                    communication_id = communication_service.send_welcome_email(
                        client_id=selected_client_id,
                        client_name=selected_client['nazwa'],
                        client_email=selected_client['email']
                    )
                    
                    if communication_id:
                        st.success("Wiadomość powitalna została wysłana!")
                    else:
                        st.error("Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.")
    
    elif template_type == "Potwierdzenie wizyty":
        with st.form("service_confirmation_form"):
            st.write("**Szablon potwierdzenia wizyty serwisowej**")
            st.write("Ten szablon jest używany do wysyłania potwierdzenia wizyty serwisowej.")
            
            # Form fields
            service_date = st.date_input("Data wizyty:", value=datetime.now())
            service_time = st.time_input("Godzina wizyty:", value=datetime.now().time())
            service_type = st.selectbox(
                "Typ usługi:",
                options=["Przegląd", "Naprawa", "Instalacja", "Konserwacja"]
            )
            technician_name = st.text_input("Imię i nazwisko technika:")
            
            # Format service date and time
            service_datetime = f"{service_date.strftime('%d.%m.%Y')} {service_time.strftime('%H:%M')}"
            
            # Preview button
            preview = st.checkbox("Podgląd szablonu")
            
            if preview:
                st.write("**Podgląd:**")
                with open("templates/email/service_confirmation.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                    html_content = html_content.replace("{{client_name}}", selected_client['nazwa'])
                    html_content = html_content.replace("{{service_date}}", service_datetime)
                    html_content = html_content.replace("{{service_type}}", service_type)
                    html_content = html_content.replace("{{technician_name}}", technician_name)
                    html_content = html_content.replace("{{current_year}}", str(datetime.now().year))
                    st.components.v1.html(html_content, height=500, scrolling=True)
            
            # Submit button
            submitted = st.form_submit_button("Wyślij potwierdzenie wizyty")
            
            if submitted:
                if not technician_name:
                    st.error("Imię i nazwisko technika jest wymagane.")
                    return
                
                with st.spinner("Wysyłanie wiadomości..."):
                    communication_id = communication_service.send_service_confirmation(
                        client_id=selected_client_id,
                        client_name=selected_client['nazwa'],
                        client_email=selected_client['email'],
                        service_date=service_datetime,
                        service_type=service_type,
                        technician_name=technician_name
                    )
                    
                    if communication_id:
                        st.success("Potwierdzenie wizyty zostało wysłane!")
                    else:
                        st.error("Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.")
    
    elif template_type == "Faktura":
        with st.form("invoice_template_form"):
            st.write("**Szablon faktury**")
            st.write("Ten szablon jest używany do wysyłania faktury.")
            
            # Form fields
            invoice_number = st.text_input("Numer faktury:")
            invoice_date = st.date_input("Data wystawienia:", value=datetime.now())
            invoice_amount = st.number_input("Kwota (PLN):", min_value=0.0, format="%.2f")
            invoice_pdf = st.file_uploader("Plik faktury (PDF):", type=["pdf"])
            
            # Format invoice date
            invoice_date_str = invoice_date.strftime('%d.%m.%Y')
            
            # Preview button
            preview = st.checkbox("Podgląd szablonu")
            
            if preview:
                st.write("**Podgląd:**")
                with open("templates/email/invoice.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                    html_content = html_content.replace("{{client_name}}", selected_client['nazwa'])
                    html_content = html_content.replace("{{invoice_number}}", invoice_number)
                    html_content = html_content.replace("{{invoice_date}}", invoice_date_str)
                    html_content = html_content.replace("{{invoice_amount}}", f"{invoice_amount:.2f}")
                    html_content = html_content.replace("{{current_year}}", str(datetime.now().year))
                    st.components.v1.html(html_content, height=500, scrolling=True)
            
            # Submit button
            submitted = st.form_submit_button("Wyślij fakturę")
            
            if submitted:
                if not invoice_number or not invoice_pdf:
                    st.error("Numer faktury i plik faktury są wymagane.")
                    return
                
                with st.spinner("Wysyłanie wiadomości..."):
                    # Read PDF file
                    invoice_pdf_bytes = invoice_pdf.read()
                    
                    communication_id = communication_service.send_invoice(
                        client_id=selected_client_id,
                        client_name=selected_client['nazwa'],
                        client_email=selected_client['email'],
                        invoice_number=invoice_number,
                        invoice_date=invoice_date_str,
                        invoice_amount=invoice_amount,
                        invoice_pdf=invoice_pdf_bytes
                    )
                    
                    if communication_id:
                        st.success("Faktura została wysłana!")
                    else:
                        st.error("Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.")
    
    elif template_type == "Oferta":
        with st.form("offer_template_form"):
            st.write("**Szablon oferty**")
            st.write("Ten szablon jest używany do wysyłania oferty.")
            
            # Form fields
            offer_number = st.text_input("Numer oferty:")
            offer_date = st.date_input("Data wystawienia:", value=datetime.now())
            offer_expiry_date = st.date_input("Data ważności:", value=datetime.now().replace(month=datetime.now().month + 1 if datetime.now().month < 12 else 1))
            offer_pdf = st.file_uploader("Plik oferty (PDF):", type=["pdf"])
            
            # Format dates
            offer_date_str = offer_date.strftime('%d.%m.%Y')
            offer_expiry_date_str = offer_expiry_date.strftime('%d.%m.%Y')
            
            # Preview button
            preview = st.checkbox("Podgląd szablonu")
            
            if preview:
                st.write("**Podgląd:**")
                with open("templates/email/offer.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                    html_content = html_content.replace("{{client_name}}", selected_client['nazwa'])
                    html_content = html_content.replace("{{offer_number}}", offer_number)
                    html_content = html_content.replace("{{offer_date}}", offer_date_str)
                    html_content = html_content.replace("{{offer_expiry_date}}", offer_expiry_date_str)
                    html_content = html_content.replace("{{current_year}}", str(datetime.now().year))
                    st.components.v1.html(html_content, height=500, scrolling=True)
            
            # Submit button
            submitted = st.form_submit_button("Wyślij ofertę")
            
            if submitted:
                if not offer_number or not offer_pdf:
                    st.error("Numer oferty i plik oferty są wymagane.")
                    return
                
                with st.spinner("Wysyłanie wiadomości..."):
                    # Read PDF file
                    offer_pdf_bytes = offer_pdf.read()
                    
                    communication_id = communication_service.send_offer(
                        client_id=selected_client_id,
                        client_name=selected_client['nazwa'],
                        client_email=selected_client['email'],
                        offer_number=offer_number,
                        offer_date=offer_date_str,
                        offer_expiry_date=offer_expiry_date_str,
                        offer_pdf=offer_pdf_bytes
                    )
                    
                    if communication_id:
                        st.success("Oferta została wysłana!")
                    else:
                        st.error("Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.")


# Helper functions
def get_clients():
    """Get all clients from the database."""
    try:
        query = "SELECT id, nazwa, email, telefon FROM klienci ORDER BY nazwa"
        result = db.execute_query(query)
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting clients: {str(e)}")
        return []


def get_client_communications(client_id, comm_type=None, limit=50, offset=0):
    """Get communications for a specific client."""
    return communication_service.CommunicationManager.get_client_communications(
        client_id=client_id,
        comm_type=comm_type,
        limit=limit,
        offset=offset
    )


def get_recent_communications(comm_type=None, direction=None, limit=10):
    """Get recent communications."""
    try:
        query = """
        SELECT k.id as id_komunikacji, k.*, c.nazwa as from_name, c.email as from_email,
               CASE WHEN k.treść LIKE '%\n%' THEN SUBSTRING(k.treść, 1, POSITION('\n' IN k.treść) - 1) ELSE k.treść END as subject
        FROM komunikacja k
        JOIN klienci c ON k.id_klienta = c.id
        WHERE 1=1
        """
        
        params = []
        
        if comm_type:
            query += " AND k.typ = %s"
            params.append(comm_type)
        
        if direction:
            query += " AND k.kierunek = %s"
            params.append(direction)
        
        query += " ORDER BY k.data_czas DESC LIMIT %s"
        params.append(limit)
        
        result = db.execute_query(query, params)
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting recent communications: {str(e)}")
        return []
