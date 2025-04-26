# HVAC CRM/ERP System

Kompleksowy system CRM/ERP dla firm HVAC (ogrzewanie, wentylacja, klimatyzacja) z zaawansowaną automatyzacją i integracją AI.

## Funkcjonalności

- **Zarządzanie klientami**: Profile klientów, historia komunikacji, ocena zamożności
- **Zarządzanie urządzeniami**: Baza urządzeń HVAC, historia serwisowa, gwarancje
- **Zlecenia serwisowe**: Planowanie, przydzielanie techników, śledzenie statusu
- **Komunikacja**: Automatyczne przetwarzanie e-maili i transkrypcji rozmów telefonicznych
- **Oferty i faktury**: Generowanie ofert, śledzenie reakcji klientów, e-podpisy
- **Wizualizacje**: Wizualizacje instalacji klimatyzacji na zdjęciach
- **Automatyzacja**: Integracja z n8n dla automatyzacji przepływów pracy
- **AI/ML**: Analiza tekstu, kategoryzacja e-maili, ocena zamożności klientów

## Technologie

- **Frontend**: Streamlit
- **Baza danych**: PostgreSQL / Supabase
- **Wektorowa baza danych**: Qdrant
- **Automatyzacja**: n8n
- **AI/ML**: Local LLM (np. Local Llama)
- **OCR**: Przetwarzanie dokumentów

## Instalacja

1. Sklonuj repozytorium:
   ```
   git clone <url-repozytorium>
   cd hvac-crm-erp
   ```

2. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

3. Skonfiguruj zmienne środowiskowe:
   Utwórz plik `.env` w głównym katalogu projektu i dodaj następujące zmienne:
   ```
   # Supabase
   SUPABASE_URL=<twój-url-supabase>
   SUPABASE_KEY=<twój-klucz-supabase>
   
   # Qdrant
   QDRANT_URL=<twój-url-qdrant>
   QDRANT_API_KEY=<twój-klucz-api-qdrant>
   QDRANT_COLLECTION=hvac_wektory
   
   # Baza danych
   DB_HOST=localhost
   DB_NAME=hvac_crm_erp
   DB_USER=hvac_admin
   DB_PASSWORD=<twoje-hasło>
   DB_PORT=5432
   
   # n8n
   N8N_URL=http://localhost:5678
   N8N_API_KEY=<twój-klucz-api-n8n>
   ```

4. Uruchom aplikację:
   ```
   streamlit run app.py
   ```

## Struktura projektu

```
hvac_crm_erp/
├── app.py                  # Główny plik aplikacji
├── requirements.txt        # Zależności
├── config.py               # Konfiguracja
├── assets/                 # Zasoby statyczne
├── components/             # Komponenty UI
├── pages/                  # Strony aplikacji
├── utils/                  # Funkcje pomocnicze
└── services/               # Logika biznesowa
```

## Rozwój

1. Zainstaluj zależności deweloperskie:
   ```
   pip install -r requirements-dev.txt
   ```

2. Uruchom testy:
   ```
   pytest
   ```

3. Sprawdź styl kodu:
   ```
   flake8
   ```

## Licencja

Ten projekt jest objęty licencją MIT.
