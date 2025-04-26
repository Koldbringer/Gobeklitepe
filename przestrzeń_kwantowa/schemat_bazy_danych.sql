-- Schemat bazy danych dla systemu HVAC CRM/ERP z elementami kwantowymi

-- Istniejąca tabela stanów kwantowych HVAC (na podstawie istniejącego kodu)
CREATE TABLE IF NOT EXISTS stany_kwantowe_hvac (
    id INTEGER PRIMARY KEY,
    temperatura DOUBLE PRECISION NOT NULL,
    wilgotność DOUBLE PRECISION NOT NULL,
    ciśnienie DOUBLE PRECISION NOT NULL,
    przepływ_powietrza DOUBLE PRECISION NOT NULL,
    stan_entanglacji DOUBLE PRECISION[] NOT NULL,
    parametry_crm JSONB NOT NULL
);

-- Tabela klientów
CREATE TABLE IF NOT EXISTS klienci (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefon VARCHAR(20),
    adres TEXT,
    typ_klienta VARCHAR(50), -- np. indywidualny, biznesowy
    data_rejestracji TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ocena_zamożności DOUBLE PRECISION, -- na podstawie analizy transkrypcji
    ostatni_kontakt TIMESTAMP,
    notatki TEXT
);

-- Tabela budynków/lokalizacji
CREATE TABLE IF NOT EXISTS budynki (
    id SERIAL PRIMARY KEY,
    id_klienta INTEGER REFERENCES klienci(id),
    nazwa VARCHAR(255) NOT NULL,
    adres TEXT NOT NULL,
    współrzędne_geo POINT, -- dla mapowania instalacji
    typ_budynku VARCHAR(50), -- np. mieszkalny, biurowy, przemysłowy
    powierzchnia DOUBLE PRECISION, -- w m²
    liczba_pięter INTEGER,
    rok_budowy INTEGER,
    notatki TEXT
);

-- Tabela urządzeń HVAC
CREATE TABLE IF NOT EXISTS urządzenia_hvac (
    id SERIAL PRIMARY KEY,
    id_budynku INTEGER REFERENCES budynki(id),
    id_stanu_kwantowego INTEGER REFERENCES stany_kwantowe_hvac(id),
    model VARCHAR(255) NOT NULL,
    numer_seryjny VARCHAR(100),
    data_instalacji DATE,
    data_ostatniego_serwisu DATE,
    status VARCHAR(50), -- np. aktywny, wyłączony, w naprawie
    lokalizacja_w_budynku TEXT,
    zdjęcie_url TEXT, -- URL do zdjęcia instalacji
    dane_techniczne JSONB -- specyfikacje techniczne urządzenia
);

-- Tabela komunikacji z klientami
CREATE TABLE IF NOT EXISTS komunikacja (
    id SERIAL PRIMARY KEY,
    id_klienta INTEGER REFERENCES klienci(id),
    typ VARCHAR(50) NOT NULL, -- np. email, telefon, SMS
    kierunek VARCHAR(10) NOT NULL, -- przychodzący/wychodzący
    data_czas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    treść TEXT,
    transkrypcja TEXT, -- dla rozmów telefonicznych
    kategoria VARCHAR(50), -- np. zapytanie, reklamacja, oferta
    status VARCHAR(50), -- np. oczekujący, odpowiedziano
    załączniki JSONB, -- linki do załączników
    analiza_sentymentu DOUBLE PRECISION, -- wynik analizy sentymentu
    klasyfikacja VARCHAR(50) -- np. ludzki, automatyczny, reklama
);

-- Tabela ofert
CREATE TABLE IF NOT EXISTS oferty (
    id SERIAL PRIMARY KEY,
    id_klienta INTEGER REFERENCES klienci(id),
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ważności DATE,
    status VARCHAR(50), -- np. wysłana, zaakceptowana, odrzucona
    wartość_netto DECIMAL(12,2),
    wartość_brutto DECIMAL(12,2),
    waluta VARCHAR(3) DEFAULT 'PLN',
    treść TEXT,
    link_do_podpisu TEXT, -- link do e-podpisu
    data_podpisania TIMESTAMP,
    notatki TEXT
);

-- Tabela reakcji na oferty
CREATE TABLE IF NOT EXISTS reakcje_oferty (
    id SERIAL PRIMARY KEY,
    id_oferty INTEGER REFERENCES oferty(id),
    typ_reakcji VARCHAR(50) NOT NULL, -- np. wyświetlenie, kliknięcie, podpisanie
    data_czas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adres_ip VARCHAR(45),
    urządzenie VARCHAR(255), -- informacje o urządzeniu klienta
    czas_spędzony INTEGER, -- czas spędzony na przeglądaniu oferty (w sekundach)
    notatki TEXT
);

-- Tabela zleceń serwisowych
CREATE TABLE IF NOT EXISTS zlecenia_serwisowe (
    id SERIAL PRIMARY KEY,
    id_urządzenia INTEGER REFERENCES urządzenia_hvac(id),
    id_klienta INTEGER REFERENCES klienci(id),
    typ_zlecenia VARCHAR(50) NOT NULL, -- np. instalacja, naprawa, przegląd
    priorytet INTEGER, -- 1-5, gdzie 5 to najwyższy
    status VARCHAR(50) NOT NULL, -- np. nowe, przypisane, w realizacji, zakończone
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_planowana DATE,
    data_realizacji DATE,
    opis_problemu TEXT,
    rozwiązanie TEXT,
    koszt DECIMAL(10,2),
    czas_realizacji INTEGER, -- w minutach
    notatki TEXT
);

-- Tabela techników/pracowników
CREATE TABLE IF NOT EXISTS pracownicy (
    id SERIAL PRIMARY KEY,
    imię VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    telefon VARCHAR(20),
    stanowisko VARCHAR(100),
    specjalizacja VARCHAR(255), -- np. klimatyzacja, ogrzewanie
    data_zatrudnienia DATE,
    status VARCHAR(50), -- np. aktywny, urlop, zwolniony
    lokalizacja_domowa POINT, -- dla planowania tras
    dostępność JSONB, -- harmonogram dostępności
    notatki TEXT
);

-- Tabela przypisań techników do zleceń
CREATE TABLE IF NOT EXISTS przypisania_zleceń (
    id SERIAL PRIMARY KEY,
    id_zlecenia INTEGER REFERENCES zlecenia_serwisowe(id),
    id_pracownika INTEGER REFERENCES pracownicy(id),
    data_przypisania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50), -- np. przypisane, zaakceptowane, odrzucone
    notatki TEXT
);

-- Tabela dostawców
CREATE TABLE IF NOT EXISTS dostawcy (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefon VARCHAR(20),
    adres TEXT,
    osoba_kontaktowa VARCHAR(255),
    warunki_współpracy TEXT,
    status VARCHAR(50), -- np. aktywny, nieaktywny
    ocena INTEGER, -- 1-5, gdzie 5 to najlepsza ocena
    notatki TEXT
);

-- Tabela produktów dostawców
CREATE TABLE IF NOT EXISTS produkty_dostawców (
    id SERIAL PRIMARY KEY,
    id_dostawcy INTEGER REFERENCES dostawcy(id),
    nazwa VARCHAR(255) NOT NULL,
    kod_produktu VARCHAR(100),
    kategoria VARCHAR(100),
    cena_netto DECIMAL(10,2),
    waluta VARCHAR(3) DEFAULT 'PLN',
    czas_dostawy INTEGER, -- w dniach
    dostępność INTEGER, -- ilość na stanie
    specyfikacja JSONB,
    notatki TEXT
);

-- Tabela płatności
CREATE TABLE IF NOT EXISTS płatności (
    id SERIAL PRIMARY KEY,
    id_klienta INTEGER REFERENCES klienci(id),
    id_oferty INTEGER REFERENCES oferty(id),
    id_zlecenia INTEGER REFERENCES zlecenia_serwisowe(id),
    kwota DECIMAL(12,2) NOT NULL,
    waluta VARCHAR(3) DEFAULT 'PLN',
    status VARCHAR(50) NOT NULL, -- np. oczekująca, opłacona, anulowana
    metoda_płatności VARCHAR(50), -- np. przelew, karta, gotówka
    data_wystawienia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    termin_płatności DATE,
    data_płatności TIMESTAMP,
    numer_faktury VARCHAR(100),
    notatki TEXT
);

-- Tabela przypomnień o płatnościach
CREATE TABLE IF NOT EXISTS przypomnienia_płatności (
    id SERIAL PRIMARY KEY,
    id_płatności INTEGER REFERENCES płatności(id),
    data_przypomnienia TIMESTAMP,
    typ VARCHAR(50), -- np. email, SMS, telefon
    status VARCHAR(50), -- np. zaplanowane, wysłane, anulowane
    treść TEXT,
    odpowiedź TEXT,
    notatki TEXT
);

-- Tabela dokumentów
CREATE TABLE IF NOT EXISTS dokumenty (
    id SERIAL PRIMARY KEY,
    typ VARCHAR(50) NOT NULL, -- np. faktura, umowa, gwarancja
    id_powiązania INTEGER, -- ID powiązanego rekordu (np. klienta, oferty)
    typ_powiązania VARCHAR(50), -- np. klient, oferta, zlecenie
    nazwa VARCHAR(255) NOT NULL,
    ścieżka_pliku TEXT NOT NULL,
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modyfikacji TIMESTAMP,
    rozmiar INTEGER, -- w bajtach
    hash VARCHAR(64), -- dla weryfikacji integralności
    treść_ocr TEXT, -- tekst wydobyty przez OCR
    metadane JSONB,
    notatki TEXT
);

-- Tabela analizy zamożności klientów
CREATE TABLE IF NOT EXISTS analiza_zamożności (
    id SERIAL PRIMARY KEY,
    id_klienta INTEGER REFERENCES klienci(id),
    źródło_danych VARCHAR(50), -- np. transkrypcja, email, zewnętrzne
    data_analizy TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    wynik_oceny DOUBLE PRECISION, -- np. skala 0-1
    pewność_oceny DOUBLE PRECISION, -- np. skala 0-1
    czynniki JSONB, -- czynniki wpływające na ocenę
    rekomendacje TEXT,
    notatki TEXT
);

-- Tabela stanów splątanych (dla urządzeń powiązanych kwantowo)
CREATE TABLE IF NOT EXISTS stany_splątane (
    id SERIAL PRIMARY KEY,
    id_urządzenia_1 INTEGER REFERENCES urządzenia_hvac(id),
    id_urządzenia_2 INTEGER REFERENCES urządzenia_hvac(id),
    stopień_splątania DOUBLE PRECISION, -- np. skala 0-1
    data_pomiaru TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parametry_splątania JSONB, -- szczegółowe parametry splątania
    wpływ_na_wydajność TEXT,
    notatki TEXT,
    CHECK (id_urządzenia_1 <> id_urządzenia_2) -- Zapobieganie splątaniu z samym sobą
);

-- Tabela wyników scrapingu ofert pracy
CREATE TABLE IF NOT EXISTS oferty_pracy (
    id SERIAL PRIMARY KEY,
    źródło VARCHAR(255), -- np. URL strony
    tytuł VARCHAR(255) NOT NULL,
    opis TEXT,
    lokalizacja VARCHAR(255),
    wynagrodzenie VARCHAR(100),
    data_publikacji DATE,
    data_scrapingu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50), -- np. nowa, przypisana, zakończona
    priorytet INTEGER, -- 1-5
    notatki TEXT
);

-- Tabela zespołów serwisowych
CREATE TABLE IF NOT EXISTS zespoły (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    lider_id INTEGER REFERENCES pracownicy(id),
    specjalizacja VARCHAR(255),
    region_działania VARCHAR(255),
    status VARCHAR(50), -- np. aktywny, nieaktywny
    notatki TEXT
);

-- Tabela członków zespołów
CREATE TABLE IF NOT EXISTS członkowie_zespołów (
    id SERIAL PRIMARY KEY,
    id_zespołu INTEGER REFERENCES zespoły(id),
    id_pracownika INTEGER REFERENCES pracownicy(id),
    rola VARCHAR(100),
    data_dołączenia DATE,
    data_opuszczenia DATE,
    notatki TEXT
);

-- Tabela zaproszeń do zespołów
CREATE TABLE IF NOT EXISTS zaproszenia_zespołów (
    id SERIAL PRIMARY KEY,
    id_zespołu INTEGER REFERENCES zespoły(id),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    data_wysłania TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ważności TIMESTAMP,
    status VARCHAR(50), -- np. wysłane, zaakceptowane, odrzucone
    notatki TEXT
);

-- Indeksy dla poprawy wydajności zapytań
CREATE INDEX idx_urządzenia_hvac_id_stanu_kwantowego ON urządzenia_hvac(id_stanu_kwantowego);
CREATE INDEX idx_komunikacja_id_klienta ON komunikacja(id_klienta);
CREATE INDEX idx_komunikacja_data_czas ON komunikacja(data_czas);
CREATE INDEX idx_zlecenia_serwisowe_status ON zlecenia_serwisowe(status);
CREATE INDEX idx_zlecenia_serwisowe_data_planowana ON zlecenia_serwisowe(data_planowana);
CREATE INDEX idx_płatności_status ON płatności(status);
CREATE INDEX idx_płatności_termin_płatności ON płatności(termin_płatności);
CREATE INDEX idx_stany_splątane_stopień_splątania ON stany_splątane(stopień_splątania);

-- Funkcja do aktualizacji daty modyfikacji dokumentów
CREATE OR REPLACE FUNCTION update_document_modified_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_modyfikacji = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_document_modified_date_trigger
BEFORE UPDATE ON dokumenty
FOR EACH ROW
EXECUTE FUNCTION update_document_modified_date();

-- Funkcja do obliczania stopnia splątania między urządzeniami
CREATE OR REPLACE FUNCTION oblicz_stopień_splątania(id_urz1 INTEGER, id_urz2 INTEGER)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    stan1 RECORD;
    stan2 RECORD;
    stopień DOUBLE PRECISION;
BEGIN
    -- Pobierz stany kwantowe obu urządzeń
    SELECT s.* INTO stan1 FROM stany_kwantowe_hvac s
    JOIN urządzenia_hvac u ON s.id = u.id_stanu_kwantowego
    WHERE u.id = id_urz1;
    
    SELECT s.* INTO stan2 FROM stany_kwantowe_hvac s
    JOIN urządzenia_hvac u ON s.id = u.id_stanu_kwantowego
    WHERE u.id = id_urz2;
    
    -- Przykładowa implementacja obliczania stopnia splątania
    -- W rzeczywistości byłaby to bardziej złożona funkcja kwantowa
    stopień := 0.5; -- Przykładowa wartość
    
    RETURN stopień;
END;
$$ LANGUAGE plpgsql;