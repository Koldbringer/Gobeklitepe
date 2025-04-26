# Instrukcja instalacji i konfiguracji systemu HVAC CRM/ERP z elementami kwantowymi

## Wymagania systemowe

- System operacyjny: Linux, Windows lub macOS
- PostgreSQL 14.0 lub nowszy z rozszerzeniem PostGIS
- Rust 1.60.0 lub nowszy
- Tokio (asynchroniczny runtime dla Rust)
- n8n dla automatyzacji przepływów pracy
- Qdrant dla wektorowej bazy danych
- Minimum 8GB RAM, zalecane 16GB
- Przestrzeń dyskowa: minimum 20GB

## Instalacja bazy danych PostgreSQL

### 1. Instalacja PostgreSQL

```bash
# Dla Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# Dla Windows - użyj instalatora ze strony https://www.postgresql.org/download/windows/
```

### 2. Konfiguracja bazy danych

```bash
# Logowanie do PostgreSQL
sudo -u postgres psql

# Tworzenie bazy danych
CREATE DATABASE hvac_crm_erp;

# Tworzenie użytkownika
CREATE USER hvac_admin WITH ENCRYPTED PASSWORD 'twoje_hasło';

# Nadanie uprawnień
GRANT ALL PRIVILEGES ON DATABASE hvac_crm_erp TO hvac_admin;

# Włączenie rozszerzenia PostGIS
\c hvac_crm_erp
CREATE EXTENSION postgis;
```

### 3. Inicjalizacja schematu bazy danych

```bash
# Importowanie schematu bazy danych
psql -U hvac_admin -d hvac_crm_erp -f schemat_bazy_danych.sql
```

## Instalacja i konfiguracja Rust

### 1. Instalacja Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# lub dla Windows - użyj instalatora ze strony https://www.rust-lang.org/tools/install
```

### 2. Instalacja zależności projektu

Utwórz plik `Cargo.toml` w katalogu głównym projektu:

```toml
[package]
name = "hvac_crm_erp_kwantowy"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.25.0", features = ["full"] }
tokio-postgres = { version = "0.7.8", features = ["with-chrono-0_4"] }
serde = { version = "1.0.152", features = ["derive"] }
serde_json = "1.0.93"
chrono = { version = "0.4.23", features = ["serde"] }
postgis = "0.9.0"
qdrant-client = "1.1.2"
```

### 3. Kompilacja projektu

```bash
cargo build --release
```

## Konfiguracja połączenia kwantowego

Aby zapewnić stabilne połączenie kwantowe między komponentami systemu, należy skonfigurować parametry entanglacji w pliku konfiguracyjnym:

### 1. Utworzenie pliku konfiguracyjnego

Utwórz plik `config_kwantowy.json` w katalogu głównym projektu:

```json
{
  "parametry_entanglacji": {
    "próg_splątania": 0.7,
    "częstotliwość_rekalibracji": 3600,
    "maksymalna_dekoherencja": 0.2,
    "wektor_bazowy": [0.5, 0.5, 0.5]
  },
  "połączenie_db": {
    "host": "localhost",
    "port": 5432,
    "dbname": "hvac_crm_erp",
    "user": "hvac_admin",
    "password": "twoje_hasło"
  },
  "qdrant": {
    "url": "http://localhost:6333",
    "collection_name": "hvac_wektory"
  },
  "n8n": {
    "webhook_url": "http://localhost:5678/webhook/",
    "api_key": "twój_klucz_api"
  }
}
```

## Instalacja i konfiguracja n8n

### 1. Instalacja n8n

```bash
npm install n8n -g
```

### 2. Uruchomienie n8n

```bash
n8n start
```

### 3. Konfiguracja przepływów pracy

Po uruchomieniu n8n, przejdź do interfejsu webowego (domyślnie http://localhost:5678) i zaimportuj przygotowane przepływy pracy z pliku `przeplywy_n8n.json`.

## Instalacja i konfiguracja Qdrant

### Konfiguracja chmurowa Qdrant
1. Edytuj plik `.env.template` i uzupełnij parametry:
```
QDRANT_CLUSTER_ID=1c169b9c-e56f-4453-ba4c-48421f4a6bf7
QDRANT_ENDPOINT=https://1c169b9c-e56f-4453-ba4c-48421f4a6bf7.eu-central-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=<twoj-klucz-API>
QDRANT_HTTPS=true
```
2. Weryfikacja połączenia:
```powershell
Invoke-RestMethod -Uri "$env:QDRANT_ENDPOINT/collections" -Headers @{"api-key"=$env:QDRANT_API_KEY}
```
3. Ustaw parametry połączenia kwantowego:
```
QUANTUM_CONNECTION_TIMEOUT=10
QUANTUM_RETRY_ATTEMPTS=3
```

Uwaga: W środowisku produkcyjnym zawsze używaj HTTPS i przechowuj klucze API w zmiennych środowiskowych!

### 1. Instalacja Qdrant

```bash
# Przy użyciu Docker
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 2. Inicjalizacja kolekcji wektorowej

```bash
curl -X PUT 'http://localhost:6333/collections/hvac_wektory' \
-H 'Content-Type: application/json' \
-d '{
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  }
}'
```

## Uruchomienie systemu

### 1. Uruchomienie serwera aplikacji

```bash
cargo run --release
```

### 2. Weryfikacja działania

Po uruchomieniu systemu, sprawdź logi, aby upewnić się, że wszystkie komponenty zostały poprawnie zainicjalizowane:

```
Inicjalizacja systemu HVAC CRM/ERP z elementami kwantowymi...
Zapisano stany kwantowe do bazy danych
Dodawanie budynku: Biurowiec Centrum
Zapisano nową komunikację o ID: 1
Analizowanie transkrypcji dla komunikacji ID: 1, klienta ID: 1
Zaktualizowano ocenę zamożności klienta ID: 1 na wartość: 0.5
Obliczono stopień splątania między urządzeniami 1 i 2: 0.75
Wysłano żądanie stanów splątanych do agenta
Inicjalizacja systemu zakończona pomyślnie!
```

## Rozwiązywanie problemów

### Problem z połączeniem do bazy danych

Sprawdź, czy usługa PostgreSQL jest uruchomiona:

```bash
sudo systemctl status postgresql
```

Upewnij się, że dane dostępowe w pliku konfiguracyjnym są poprawne.

### Problem ze stabilnością połączenia kwantowego

Jeśli występują problemy ze stabilnością połączenia kwantowego, spróbuj zrekalibrować parametry entanglacji:

```bash
cargo run --bin rekalibracja_kwantowa
```

### Problem z wydajnością systemu

Jeśli system działa wolno, rozważ zwiększenie limitu pamięci dla Qdrant i PostgreSQL w plikach konfiguracyjnych.

## Konserwacja systemu

### Regularne kopie zapasowe

Skonfiguruj regularne kopie zapasowe bazy danych:

```bash
# Dodaj do crontab
0 2 * * * pg_dump -U hvac_admin -d hvac_crm_erp > /path/to/backup/hvac_backup_$(date +\%Y\%m\%d).sql
```

### Monitorowanie stanu splątania

Regularnie monitoruj stan splątania między urządzeniami, aby wykryć potencjalne problemy:

```bash
cargo run --bin monitor_splątania
```

### Aktualizacja systemu

Aby zaktualizować system do najnowszej wersji:

```bash
git pull
cargo build --release
```

## Uwagi końcowe

Pamiętaj, że stabilność połączenia kwantowego jest kluczowa dla prawidłowego działania systemu. Regularnie monitoruj parametry entanglacji i w razie potrzeby przeprowadzaj rekalibrację. W przypadku wystąpienia dekoherencji kwantowej, system automatycznie podejmie próbę przywrócenia stabilności, ale w niektórych przypadkach może być wymagana manualna interwencja.