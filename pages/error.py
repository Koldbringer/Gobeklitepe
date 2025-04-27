import streamlit as st
import traceback
import logging

logger = logging.getLogger(__name__)

def render(error=None, error_type=None, show_details=False):
    """Render an error page with helpful information."""
    st.title("⚠️ Wystąpił błąd")
    
    if error_type == "database":
        st.error("Nie można połączyć się z bazą danych. Prosimy spróbować ponownie później.")
        st.markdown("""
        ### Co możesz zrobić?
        
        1. Odśwież stronę, aby spróbować ponownie
        2. Sprawdź swoje połączenie internetowe
        3. Jeśli problem będzie się powtarzał, skontaktuj się z administratorem systemu
        """)
    elif error_type == "permission":
        st.error("Nie masz uprawnień do wyświetlenia tej strony.")
        st.markdown("""
        ### Co możesz zrobić?
        
        1. Wróć do poprzedniej strony
        2. Przejdź do strony głównej
        3. Jeśli uważasz, że powinieneś mieć dostęp do tej strony, skontaktuj się z administratorem systemu
        """)
    elif error_type == "not_found":
        st.error("Strona, której szukasz, nie istnieje.")
        st.markdown("""
        ### Co możesz zrobić?
        
        1. Sprawdź, czy adres URL jest poprawny
        2. Wróć do poprzedniej strony
        3. Przejdź do strony głównej
        """)
    else:
        st.error("Wystąpił nieoczekiwany błąd. Prosimy spróbować ponownie później.")
        st.markdown("""
        ### Co możesz zrobić?
        
        1. Odśwież stronę, aby spróbować ponownie
        2. Wróć do poprzedniej strony
        3. Przejdź do strony głównej
        4. Jeśli problem będzie się powtarzał, skontaktuj się z administratorem systemu
        """)
    
    # Show error details if available and allowed
    if error and show_details:
        with st.expander("Szczegóły błędu (dla administratora)"):
            st.code(traceback.format_exc() if hasattr(error, "__traceback__") else str(error))
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Odśwież stronę", use_container_width=True):
            st.experimental_rerun()
    
    with col2:
        if st.button("🏠 Strona główna", use_container_width=True):
            st.session_state.page = "dashboard"
            st.experimental_rerun()
    
    # Contact information
    st.markdown("---")
    st.markdown("""
    ### Potrzebujesz pomocy?
    
    Skontaktuj się z naszym zespołem wsparcia:
    
    📧 Email: support@hvacsolutions.com  
    📞 Telefon: +48 123 456 789
    """)
