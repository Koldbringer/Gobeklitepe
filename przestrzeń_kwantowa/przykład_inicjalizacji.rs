use std::sync::{Arc, Mutex};
use tokio;
use chrono::Utc;
use serde_json::json;

// Importy z naszego projektu
use crate::stan_kwantowy_postgres::{MenedżerStanuKwantowego, StanKwantowyHVAC, ParametryCRM};
use crate::agent_komunikacja::{AgentHVAC, KomunikatAgenta};
use crate::crm_erp_postgres::{MenedżerCRMERP, Klient, Budynek, UrządzenieHVAC, Komunikacja};
use crate::integracja_crm_kwantowa::{IntegratorCRMKwantowy, KomunikatCRM};

// Przykładowa funkcja inicjalizująca system
pub async fn inicjalizuj_system() -> Result<(), Box<dyn std::error::Error>> {
    println!("Inicjalizacja systemu HVAC CRM/ERP z elementami kwantowymi...");
    
    // Parametry połączenia do bazy danych
    let connection_string = "host=localhost dbname=hvac_crm_erp user=postgres password=hasło";
    
    // Inicjalizacja menedżera stanu kwantowego
    let menedżer_stanu = Arc::new(Mutex::new(
        MenedżerStanuKwantowego::nowy(connection_string).await?
    ));
    
    // Inicjalizacja menedżera CRM/ERP
    let menedżer_crm = Arc::new(Mutex::new(
        MenedżerCRMERP::nowy(connection_string, Arc::clone(&menedżer_stanu)).await?
    ));
    
    // Inicjalizacja integratora
    let mut integrator = IntegratorCRMKwantowy::nowy(
        Arc::clone(&menedżer_crm),
        Arc::clone(&menedżer_stanu)
    );
    
    // Tworzenie przykładowych stanów kwantowych dla urządzeń HVAC
    let stan_kwantowy_1 = StanKwantowyHVAC {
        id: 1,
        temperatura: 22.5,
        wilgotność: 45.0,
        ciśnienie: 1013.2,
        przepływ_powietrza: 150.0,
        stan_entanglacji: vec![0.8, 0.2, 0.5],
        parametry_crm: ParametryCRM {
            id_klienta: 1,
            priorytet_serwisu: 2,
            historia_serwisowa: Vec::new(),
            predykcje_awarii: Vec::new(),
            odczyty_sensorow_kwantowych: vec![0.9, 0.3, 0.7],
        },
    };
    
    let stan_kwantowy_2 = StanKwantowyHVAC {
        id: 2,
        temperatura: 24.0,
        wilgotność: 50.0,
        ciśnienie: 1012.8,
        przepływ_powietrza: 180.0,
        stan_entanglacji: vec![0.2, 0.8, 0.5],
        parametry_crm: ParametryCRM {
            id_klienta: 2,
            priorytet_serwisu: 1,
            historia_serwisowa: Vec::new(),
            predykcje_awarii: Vec::new(),
            odczyty_sensorow_kwantowych: vec![0.3, 0.9, 0.7],
        },
    };
    
    // Zapisanie stanów kwantowych do bazy danych
    {
        let mut menedżer = menedżer_stanu.lock().unwrap();
        menedżer.zapisz_stan(stan_kwantowy_1.clone()).await?;
        menedżer.zapisz_stan(stan_kwantowy_2.clone()).await?;
        println!("Zapisano stany kwantowe do bazy danych");
    }
    
    // Tworzenie agentów HVAC
    let agent_1 = Arc::new(Mutex::new(
        AgentHVAC::nowy("Agent-1".to_string(), stan_kwantowy_1, Arc::clone(&menedżer_stanu)).await
    ));
    
    let agent_2 = Arc::new(Mutex::new(
        AgentHVAC::nowy("Agent-2".to_string(), stan_kwantowy_2, Arc::clone(&menedżer_stanu)).await
    ));
    
    // Dodanie agentów do integratora
    integrator.dodaj_agenta(Arc::clone(&agent_1));
    integrator.dodaj_agenta(Arc::clone(&agent_2));
    
    // Przykładowe dane klienta
    let klient = Klient {
        id: 0, // ID zostanie przypisane przez bazę danych
        nazwa: "Firma XYZ Sp. z o.o.".to_string(),
        email: Some("kontakt@firmaxyz.pl".to_string()),
        telefon: Some("+48 123 456 789".to_string()),
        adres: Some("ul. Przykładowa 123, 00-001 Warszawa".to_string()),
        typ_klienta: Some("biznesowy".to_string()),
        data_rejestracji: Utc::now(),
        ocena_zamożności: Some(0.75),
        ostatni_kontakt: Some(Utc::now()),
        notatki: Some("Klient zainteresowany systemami HVAC dla biurowca".to_string()),
    };
    
    // Dodanie klienta do systemu
    let komunikat_klient = KomunikatCRM::NowyKlient(klient);
    integrator.przetwórz_komunikat_crm(komunikat_klient).await?;
    
    // Przykładowe dane budynku
    let budynek = Budynek {
        id: 0,
        id_klienta: 1, // Zakładamy, że klient otrzymał ID 1
        nazwa: "Biurowiec Centrum".to_string(),
        adres: "ul. Centralna 1, 00-001 Warszawa".to_string(),
        współrzędne_geo: Some((21.0122, 52.2297)), // Długość i szerokość geograficzna
        typ_budynku: Some("biurowy".to_string()),
        powierzchnia: Some(5000.0),
        liczba_pięter: Some(10),
        rok_budowy: Some(2015),
        notatki: Some("Nowoczesny biurowiec klasy A".to_string()),
    };
    
    // Dodanie budynku do bazy danych (w praktyce potrzebna byłaby metoda w MenedżerCRMERP)
    println!("Dodawanie budynku: {}", budynek.nazwa);
    
    // Przykładowe urządzenie HVAC
    let urządzenie = UrządzenieHVAC {
        id: 0,
        id_budynku: 1, // Zakładamy, że budynek otrzymał ID 1
        id_stanu_kwantowego: 1,
        model: "SuperCool 3000".to_string(),
        numer_seryjny: Some("SC3000-12345".to_string()),
        data_instalacji: Some(Utc::now()),
        data_ostatniego_serwisu: Some(Utc::now()),
        status: "aktywny".to_string(),
        lokalizacja_w_budynku: Some("Piętro 5, serwerownia".to_string()),
        zdjęcie_url: Some("https://example.com/images/sc3000.jpg".to_string()),
        dane_techniczne: Some(json!({
            "moc_chłodnicza": 5.2,
            "moc_grzewcza": 6.0,
            "poziom_hałasu": 32,
            "klasa_energetyczna": "A++"
        })),
    };
    
    // Dodanie urządzenia do systemu
    let komunikat_urządzenie = KomunikatCRM::NoweUrządzenie(urządzenie);
    integrator.przetwórz_komunikat_crm(komunikat_urządzenie).await?;
    
    // Przykładowa komunikacja z klientem (transkrypcja rozmowy telefonicznej)
    let komunikacja = Komunikacja {
        id: 0,
        id_klienta: 1,
        typ: "telefon".to_string(),
        kierunek: "przychodzący".to_string(),
        data_czas: Utc::now(),
        treść: None,
        transkrypcja: Some("Dzień dobry, dzwonię w sprawie serwisu klimatyzacji w naszej rezydencji. \
                           Chciałbym zamówić przegląd wszystkich urządzeń przed sezonem letnim. \
                           Zależy mi na szybkiej realizacji, jestem gotów zapłacić więcej za priorytetową usługę. \
                           Mamy też luksusowy apartament w górach, tam również potrzebujemy serwisu.".to_string()),
        kategoria: Some("serwis".to_string()),
        status: "nowy".to_string(),
        załączniki: None,
        analiza_sentymentu: None,
        klasyfikacja: Some("ludzki".to_string()),
    };
    
    // Dodanie komunikacji do systemu i analiza transkrypcji
    let komunikat_komunikacja = KomunikatCRM::NowaKomunikacja(komunikacja);
    integrator.przetwórz_komunikat_crm(komunikat_komunikacja).await?;
    
    // Obliczenie stopnia splątania między urządzeniami
    let komunikat_splątanie = KomunikatCRM::ŻądanieObliczeniaSplątania {
        id_urządzenia_1: 1,
        id_urządzenia_2: 2,
    };
    integrator.przetwórz_komunikat_crm(komunikat_splątanie).await?;
    
    // Symulacja żądania stanów splątanych od agenta
    {
        let mut agent = agent_1.lock().unwrap();
        let komunikat = KomunikatAgenta::ŻądanieStanówSplątanych { prog_entanglacji: 0.5 };
        agent.przetwórz_komunikat(komunikat).await;
        println!("Wysłano żądanie stanów splątanych do agenta");
    }
    
    println!("Inicjalizacja systemu zakończona pomyślnie!");
    Ok(())
}

// Przykładowa funkcja główna do testowania
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    inicjalizuj_system().await?;
    Ok(())
}