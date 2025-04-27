"""
Voice Interface Page for HVAC CRM/ERP System

This page provides a voice-based interface for interacting with the system,
including text-to-speech, speech-to-text, and voice message generation.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import base64
from io import BytesIO

from services import voice_communication
from utils import db

logger = logging.getLogger(__name__)

def render():
    """Render the voice interface page."""
    st.title("🎙️ Interfejs głosowy")
    
    # Check if voice functionality is enabled
    if not voice_communication.ENABLE_VOICE:
        st.warning("Funkcjonalność głosowa jest wyłączona. Włącz ją w ustawieniach, aby korzystać z interfejsu głosowego.")
        
        with st.expander("Jak włączyć funkcjonalność głosową?"):
            st.markdown("""
            Aby włączyć funkcjonalność głosową, należy:
            
            1. Dodać klucz API ElevenLabs do pliku `.env`:
               ```
               ELEVENLABS_API_KEY=your_api_key
               ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1
               ENABLE_VOICE=true
               ```
            
            2. Zrestartować aplikację
            
            Możesz uzyskać klucz API na stronie [ElevenLabs](https://elevenlabs.io/).
            """)
        
        return
    
    # Create tabs for different voice features
    tab1, tab2, tab3 = st.tabs(["Wiadomości głosowe", "Konwersja tekstu na mowę", "Asystent głosowy"])
    
    with tab1:
        render_voice_messages()
    
    with tab2:
        render_text_to_speech()
    
    with tab3:
        render_voice_assistant()


def render_voice_messages():
    """Render the voice messages tab."""
    st.subheader("Wiadomości głosowe")
    
    # Get clients for dropdown
    clients = get_clients()
    
    if not clients:
        st.warning("Brak klientów w bazie danych. Dodaj klienta, aby wysłać wiadomość głosową.")
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
    
    # Voice selection
    voices = voice_communication.TextToSpeech.get_available_voices()
    
    if not voices:
        st.warning("Nie można pobrać dostępnych głosów. Sprawdź klucz API ElevenLabs.")
        voice_id = voice_communication.DEFAULT_VOICE_ID
    else:
        voice_id = st.selectbox(
            "Wybierz głos:",
            options=[voice['voice_id'] for voice in voices],
            format_func=lambda x: next((f"{voice['name']} ({voice['category']})" for voice in voices if voice['voice_id'] == x), "")
        )
    
    # Message form
    with st.form("voice_message_form"):
        message = st.text_area("Treść wiadomości głosowej:", height=150)
        
        # Advanced options
        with st.expander("Zaawansowane opcje głosu"):
            col1, col2 = st.columns(2)
            
            with col1:
                stability = st.slider("Stabilność:", 0.0, 1.0, voice_communication.DEFAULT_STABILITY)
                style = st.slider("Styl:", 0.0, 1.0, voice_communication.DEFAULT_STYLE)
            
            with col2:
                similarity_boost = st.slider("Podobieństwo:", 0.0, 1.0, voice_communication.DEFAULT_SIMILARITY_BOOST)
                speaker_boost = st.checkbox("Wzmocnienie mówcy", value=voice_communication.DEFAULT_USE_SPEAKER_BOOST)
        
        # Submit button
        submitted = st.form_submit_button("Generuj wiadomość głosową")
        
        if submitted:
            if not message:
                st.error("Treść wiadomości jest wymagana.")
                return
            
            # Generate voice message
            with st.spinner("Generowanie wiadomości głosowej..."):
                result = voice_communication.generate_voice_message(
                    client_id=selected_client_id,
                    text=message,
                    voice_id=voice_id
                )
                
                if result.get("success"):
                    st.success("Wiadomość głosowa została wygenerowana!")
                    
                    # Display audio player
                    st.audio(result["data_uri"])
                    
                    # Display message details
                    st.write(f"**ID komunikacji:** {result['communication_id']}")
                    st.write(f"**Ścieżka pliku:** {result['file_path']}")
                    
                    # Add send button
                    if st.button("Wyślij wiadomość głosową do klienta"):
                        st.info("Funkcjonalność wysyłania wiadomości głosowych jest w trakcie implementacji.")
                else:
                    st.error(f"Wystąpił błąd podczas generowania wiadomości głosowej: {result.get('error', 'Nieznany błąd')}")
    
    # Display recent voice messages
    st.subheader("Ostatnie wiadomości głosowe")
    
    # Get recent voice messages (placeholder)
    voice_messages = get_voice_messages(client_id=selected_client_id)
    
    if not voice_messages:
        st.info("Brak wiadomości głosowych dla wybranego klienta.")
    else:
        for msg in voice_messages:
            with st.expander(f"{msg['data_czas'].strftime('%d.%m.%Y %H:%M')} - {msg['treść'][:50]}..."):
                st.write(f"**Data:** {msg['data_czas'].strftime('%d.%m.%Y %H:%M')}")
                st.write(f"**Treść:** {msg['treść']}")
                
                # Display audio player if available
                if msg.get('załączniki'):
                    try:
                        attachments = eval(msg['załączniki'])
                        for attachment in attachments:
                            if attachment.get('file_path'):
                                st.audio(attachment['file_path'])
                    except:
                        st.warning("Nie można wyświetlić załącznika audio.")


def render_text_to_speech():
    """Render the text-to-speech tab."""
    st.subheader("Konwersja tekstu na mowę")
    
    # Voice selection
    voices = voice_communication.TextToSpeech.get_available_voices()
    
    if not voices:
        st.warning("Nie można pobrać dostępnych głosów. Sprawdź klucz API ElevenLabs.")
        voice_id = voice_communication.DEFAULT_VOICE_ID
    else:
        voice_id = st.selectbox(
            "Wybierz głos:",
            options=[voice['voice_id'] for voice in voices],
            format_func=lambda x: next((f"{voice['name']} ({voice['category']})" for voice in voices if voice['voice_id'] == x), ""),
            key="tts_voice_select"
        )
    
    # Text input
    text = st.text_area("Wprowadź tekst do konwersji:", height=150)
    
    # Advanced options
    with st.expander("Zaawansowane opcje głosu"):
        col1, col2 = st.columns(2)
        
        with col1:
            stability = st.slider(
                "Stabilność:",
                0.0, 1.0, voice_communication.DEFAULT_STABILITY,
                key="tts_stability"
            )
            style = st.slider(
                "Styl:",
                0.0, 1.0, voice_communication.DEFAULT_STYLE,
                key="tts_style"
            )
        
        with col2:
            similarity_boost = st.slider(
                "Podobieństwo:",
                0.0, 1.0, voice_communication.DEFAULT_SIMILARITY_BOOST,
                key="tts_similarity"
            )
            speaker_boost = st.checkbox(
                "Wzmocnienie mówcy",
                value=voice_communication.DEFAULT_USE_SPEAKER_BOOST,
                key="tts_speaker_boost"
            )
    
    # Generate button
    if st.button("Generuj mowę"):
        if not text:
            st.error("Wprowadź tekst do konwersji.")
            return
        
        with st.spinner("Generowanie mowy..."):
            # Generate speech
            audio_data = voice_communication.TextToSpeech.generate_speech(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=speaker_boost
            )
            
            if audio_data:
                # Convert to data URI
                data_uri = voice_communication.TextToSpeech.get_audio_data_uri(audio_data)
                
                # Display audio player
                st.audio(data_uri)
                
                # Add download button
                st.download_button(
                    label="Pobierz plik audio",
                    data=audio_data,
                    file_name=f"speech_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3",
                    mime="audio/mpeg"
                )
            else:
                st.error("Wystąpił błąd podczas generowania mowy.")


def render_voice_assistant():
    """Render the voice assistant tab."""
    st.subheader("Asystent głosowy")
    
    st.markdown("""
    Asystent głosowy pozwala na interakcję z systemem za pomocą głosu. Możesz zadawać pytania,
    wydawać polecenia i otrzymywać odpowiedzi głosowe.
    
    **Funkcje asystenta:**
    - Odpowiadanie na pytania o klientów, urządzenia, zlecenia
    - Tworzenie nowych zleceń serwisowych
    - Wyszukiwanie informacji w bazie danych
    - Generowanie raportów głosowych
    """)
    
    # Placeholder for voice input
    st.info("Funkcjonalność asystenta głosowego jest w trakcie implementacji.")
    
    # Simulate voice assistant interaction
    st.write("**Przykładowe komendy:**")
    
    example_commands = [
        "Pokaż mi listę klientów",
        "Jakie mamy zlecenia serwisowe na dzisiaj?",
        "Utwórz nowe zlecenie serwisowe dla klienta Jan Kowalski",
        "Jaki jest status zlecenia numer 123?",
        "Wygeneruj raport miesięczny"
    ]
    
    selected_command = st.selectbox("Wybierz przykładową komendę:", example_commands)
    
    if st.button("Symuluj komendę głosową"):
        with st.spinner("Przetwarzanie komendy głosowej..."):
            # Simulate processing time
            import time
            time.sleep(2)
            
            # Display response based on command
            if "listę klientów" in selected_command:
                st.write("**Odpowiedź asystenta:**")
                st.write("Oto lista klientów:")
                
                # Get sample clients
                clients = get_clients(limit=5)
                if clients:
                    for client in clients:
                        st.write(f"- {client['nazwa']} ({client['email']})")
                else:
                    st.write("Brak klientów w bazie danych.")
                
                # Generate voice response
                generate_assistant_response("Oto lista klientów. Wyświetlam 5 najnowszych klientów w systemie.")
            
            elif "zlecenia serwisowe na dzisiaj" in selected_command:
                st.write("**Odpowiedź asystenta:**")
                st.write("Na dzisiaj masz zaplanowane 3 zlecenia serwisowe:")
                st.write("1. Przegląd klimatyzacji - Jan Kowalski - 10:00")
                st.write("2. Naprawa pompy ciepła - Anna Nowak - 13:30")
                st.write("3. Instalacja nowego systemu - Firma XYZ - 16:00")
                
                # Generate voice response
                generate_assistant_response("Na dzisiaj masz zaplanowane 3 zlecenia serwisowe. Przegląd klimatyzacji u Jana Kowalskiego o 10:00, naprawa pompy ciepła u Anny Nowak o 13:30, oraz instalacja nowego systemu w Firmie XYZ o 16:00.")
            
            elif "nowe zlecenie" in selected_command:
                st.write("**Odpowiedź asystenta:**")
                st.write("Tworzę nowe zlecenie serwisowe dla klienta Jan Kowalski.")
                st.write("Jakiego typu ma być to zlecenie? Przegląd, naprawa czy instalacja?")
                
                # Simulate user response
                zlecenie_typ = st.radio("Wybierz typ zlecenia:", ["Przegląd", "Naprawa", "Instalacja"])
                
                if st.button("Kontynuuj"):
                    st.write(f"**Odpowiedź asystenta:**")
                    st.write(f"Utworzono nowe zlecenie serwisowe typu {zlecenie_typ} dla klienta Jan Kowalski.")
                    st.write("Zlecenie zostało zaplanowane na jutro o 12:00.")
                    
                    # Generate voice response
                    generate_assistant_response(f"Utworzono nowe zlecenie serwisowe typu {zlecenie_typ} dla klienta Jan Kowalski. Zlecenie zostało zaplanowane na jutro o 12:00.")
            
            elif "status zlecenia" in selected_command:
                st.write("**Odpowiedź asystenta:**")
                st.write("Zlecenie numer 123 ma status: W trakcie realizacji")
                st.write("Technik: Adam Wiśniewski")
                st.write("Planowane zakończenie: dzisiaj o 15:30")
                
                # Generate voice response
                generate_assistant_response("Zlecenie numer 123 ma status: W trakcie realizacji. Technik Adam Wiśniewski pracuje nad nim i planowane zakończenie to dzisiaj o 15:30.")
            
            elif "raport" in selected_command:
                st.write("**Odpowiedź asystenta:**")
                st.write("Generuję raport miesięczny...")
                
                # Display sample chart
                import numpy as np
                import pandas as pd
                import plotly.express as px
                
                # Sample data
                dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
                values = np.random.randint(1, 10, size=len(dates))
                df = pd.DataFrame({'Data': dates, 'Liczba zleceń': values})
                
                # Create chart
                fig = px.line(df, x='Data', y='Liczba zleceń', title='Liczba zleceń w styczniu 2023')
                st.plotly_chart(fig)
                
                # Generate voice response
                generate_assistant_response("Wygenerowałem raport miesięczny za styczeń 2023. W tym miesiącu zrealizowano łącznie 156 zleceń serwisowych, co stanowi wzrost o 12% w porównaniu do poprzedniego miesiąca.")


# Helper functions
def get_clients(limit=None):
    """Get clients from the database."""
    try:
        query = "SELECT id, nazwa, email, telefon FROM klienci ORDER BY nazwa"
        if limit:
            query += f" LIMIT {limit}"
        
        result = db.execute_query(query)
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting clients: {str(e)}")
        return []


def get_voice_messages(client_id=None, limit=5):
    """Get voice messages from the database."""
    try:
        query = """
        SELECT * FROM komunikacja
        WHERE typ = 'voice'
        """
        
        params = []
        
        if client_id:
            query += " AND id_klienta = %s"
            params.append(client_id)
        
        query += " ORDER BY data_czas DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        result = db.execute_query(query, params)
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting voice messages: {str(e)}")
        return []


def generate_assistant_response(text):
    """Generate and display a voice response from the assistant."""
    try:
        # Generate speech
        audio_data = voice_communication.TextToSpeech.generate_speech(
            text=text,
            voice_id=voice_communication.DEFAULT_VOICE_ID
        )
        
        if audio_data:
            # Convert to data URI
            data_uri = voice_communication.TextToSpeech.get_audio_data_uri(audio_data)
            
            # Display audio player
            st.audio(data_uri)
        else:
            st.error("Nie można wygenerować odpowiedzi głosowej.")
    except Exception as e:
        logger.error(f"Error generating assistant response: {str(e)}")
        st.error("Wystąpił błąd podczas generowania odpowiedzi głosowej.")
