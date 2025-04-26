use std::sync::{Arc, Mutex};
use tokio::sync::mpsc::{channel, Sender, Receiver};
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};

use crate::integracja_crm_kwantowa::{IntegratorCRMKwantowy, KomunikatCRM};
use crate::stan_kwantowy_postgres::{MenedżerStanuKwantowego, StanKwantowyHVAC};
use crate::crm_erp_postgres::{MenedżerCRMERP, Komunikacja, Klient, UrządzenieHVAC, Budynek};
use crate::interfejs_wizualizacji::InterfejsWizualizacji;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum KomendaInterfejsu {
    DodajKlienta(Klient),
    DodajUrządzenie(UrządzenieHVAC),
    DodajBudynek(Budynek),
    ZapiszKomunikację(Komunikacja),
    AnalizujTranskrypcję {
        id_komunikacji: i32,
        id_klienta: i32,
        transkrypcja: String,
    },
    ObliczSplątanie {
        id_urządzenia_1: i32,
        id_urządzenia_2: i32,
    },
    WyświetlMapęInstalacji {
        id_klienta: Option<i32>,
        region: Option<String>,
    },
    MonitorujStanKwantowy(i32), // ID urządzenia
    RekalibrujPołączenieKwantowe(i32), // ID urządzenia
    WyświetlDashboard,
    WyświetlHistorięSerwisową(i32), // ID urządzenia
    WyświetlOcenęZamożnościKlienta(i32), // ID klienta
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OdpowiedźInterfejsu {
    Sukces(String),
    Błąd(String),
    DaneSplątania {
        id_urządzenia_1: i32,
        id_urządzenia_2: i32,
        stopień_splątania: f64,
    },
    StanKwantowy(StanKwantowyHVAC),
    DaneKlienta(Klient),
    DaneUrządzenia(UrządzenieHVAC),
    DaneBudynku(Budynek),
    HistoriaSerwisowa(Vec<HistoriaSerwisowa>),
    OcenaZamożności {
        id_klienta: i32,
        ocena: f64,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HistoriaSerwisowa {
    pub id: i32,
    pub id_urządzenia: i32,
    pub data_serwisu: DateTime<Utc>,
    pub opis: String,
    pub wykonane_czynności: Vec<String>,
    pub stan_przed: Option<StanKwantowyHVAC>,
    pub stan_po: Option<StanKwantowyHVAC>,
}

pub struct InterfejsUżytkownika {
    integrator: Arc<IntegratorCRMKwantowy>,
    menedżer_crm: Arc<Mutex<MenedżerCRMERP>>,
    menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>,
    interfejs_wizualizacji: Arc<Mutex<InterfejsWizualizacji>>,
    nadajnik_komend: Sender<KomendaInterfejsu>,
    odbiornik_odpowiedzi: Receiver<OdpowiedźInterfejsu>,
    stan_połączenia_kwantowego: f64, // 0.0 - 1.0, gdzie 1.0 to pełna stabilność
}

impl InterfejsUżytkownika {
    pub fn nowy(
        integrator: Arc<IntegratorCRMKwantowy>,
        menedżer_crm: Arc<Mutex<MenedżerCRMERP>>,
        menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>,
        interfejs_wizualizacji: Arc<Mutex<InterfejsWizualizacji>>,
    ) -> Self {
        let (nadajnik_komend, odbiornik_komend) = channel(100);
        let (nadajnik_odpowiedzi, odbiornik_odpowiedzi) = channel(100);
        
        // Uruchomienie pętli obsługi komend w osobnym wątku
        let integrator_clone = integrator.clone();
        let menedżer_crm_clone = menedżer_crm.clone();
        let menedżer_stanu_clone = menedżer_stanu.clone();
        let nadajnik_odpowiedzi_clone = nadajnik_odpowiedzi.clone();
        
        tokio::spawn(async move {
            Self::pętla_obsługi_komend(
                odbiornik_komend,
                nadajnik_odpowiedzi_clone,
                integrator_clone,
                menedżer_crm_clone,
                menedżer_stanu_clone,
            ).await;
        });
        
        Self {
            integrator,
            menedżer_crm,
            menedżer_stanu,
            interfejs_wizualizacji,
            nadajnik_komend,
            odbiornik_odpowiedzi,
            stan_połączenia_kwantowego: 1.0, // Początkowa wartość - pełna stabilność
        }
    }
    
    async fn pętla_obsługi_komend(
        mut odbiornik: Receiver<KomendaInterfejsu>,
        nadajnik: Sender<OdpowiedźInterfejsu>,
        integrator: Arc<IntegratorCRMKwantowy>,
        menedżer_crm: Arc<Mutex<MenedżerCRMERP>>,
        menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>,
    ) {
        while let Some(komenda) = odbiornik.recv().await {
            let odpowiedź = match komenda {
                KomendaInterfejsu::DodajKlienta(klient) => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::NowyKlient(klient.clone())).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces(format!("Dodano klienta: {}", klient.nazwa)),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd dodawania klienta: {}", e)),
                    }
                },
                KomendaInterfejsu::DodajUrządzenie(urządzenie) => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::NoweUrządzenie(urządzenie.clone())).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces(format!("Dodano urządzenie: {}", urządzenie.model)),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd dodawania urządzenia: {}", e)),
                    }
                },
                KomendaInterfejsu::ZapiszKomunikację(komunikacja) => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::NowaKomunikacja(komunikacja)).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces("Zapisano komunikację".to_string()),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd zapisywania komunikacji: {}", e)),
                    }
                },
                KomendaInterfejsu::AnalizujTranskrypcję { id_komunikacji, id_klienta, transkrypcja } => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::ŻądanieAnalizyTranskrypcji {
                        id_komunikacji,
                        transkrypcja,
                    }).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces(format!("Analizowano transkrypcję dla klienta ID: {}", id_klienta)),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd analizy transkrypcji: {}", e)),
                    }
                },
                KomendaInterfejsu::ObliczSplątanie { id_urządzenia_1, id_urządzenia_2 } => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::ŻądanieObliczeniaSplątania {
                        id_urządzenia_1,
                        id_urządzenia_2,
                    }).await {
                        Ok(_) => {
                            // Tutaj powinniśmy pobrać wynik obliczenia splątania
                            let menedżer_crm_guard = menedżer_crm.lock().unwrap();
                            match menedżer_crm_guard.pobierz_stopień_splątania(id_urządzenia_1, id_urządzenia_2).await {
                                Ok(stopień) => OdpowiedźInterfejsu::DaneSplątania {
                                    id_urządzenia_1,
                                    id_urządzenia_2,
                                    stopień_splątania: stopień,
                                },
                                Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd pobierania stopnia splątania: {}", e)),
                            }
                        },
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd obliczania splątania: {}", e)),
                    }
                },
                KomendaInterfejsu::WyświetlMapęInstalacji { id_klienta, region } => {
                    match integrator.przetwórz_komunikat_crm(KomunikatCRM::ŻądanieMapyInstalacji {
                        id_klienta,
                        region,
                    }).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces("Wygenerowano mapę instalacji".to_string()),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd generowania mapy: {}", e)),
                    }
                },
                KomendaInterfejsu::MonitorujStanKwantowy(id_urządzenia) => {
                    let menedżer_stanu_guard = menedżer_stanu.lock().unwrap();
                    match menedżer_stanu_guard.pobierz_stan(id_urządzenia).await {
                        Ok(stan) => OdpowiedźInterfejsu::StanKwantowy(stan),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd pobierania stanu kwantowego: {}", e)),
                    }
                },
                KomendaInterfejsu::RekalibrujPołączenieKwantowe(id_urządzenia) => {
                    let menedżer_stanu_guard = menedżer_stanu.lock().unwrap();
                    match menedżer_stanu_guard.rekalibruj_stan(id_urządzenia).await {
                        Ok(_) => OdpowiedźInterfejsu::Sukces(format!("Zrekalibrowano połączenie kwantowe dla urządzenia ID: {}", id_urządzenia)),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd rekalibracji: {}", e)),
                    }
                },
                KomendaInterfejsu::WyświetlDashboard => {
                    // Tutaj można zaimplementować logikę pobierania danych do dashboardu
                    OdpowiedźInterfejsu::Sukces("Wyświetlono dashboard".to_string())
                },
                KomendaInterfejsu::WyświetlHistorięSerwisową(id_urządzenia) => {
                    let menedżer_crm_guard = menedżer_crm.lock().unwrap();
                    match menedżer_crm_guard.pobierz_historię_serwisową(id_urządzenia).await {
                        Ok(historia) => OdpowiedźInterfejsu::HistoriaSerwisowa(historia),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd pobierania historii serwisowej: {}", e)),
                    }
                },
                KomendaInterfejsu::WyświetlOcenęZamożnościKlienta(id_klienta) => {
                    let menedżer_crm_guard = menedżer_crm.lock().unwrap();
                    match menedżer_crm_guard.pobierz_ocenę_zamożności(id_klienta).await {
                        Ok(ocena) => OdpowiedźInterfejsu::OcenaZamożności {
                            id_klienta,
                            ocena,
                        },
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd pobierania oceny zamożności: {}", e)),
                    }
                },
                KomendaInterfejsu::DodajBudynek(budynek) => {
                    let menedżer_crm_guard = menedżer_crm.lock().unwrap();
                    match menedżer_crm_guard.dodaj_budynek(&budynek).await {
                        Ok(id) => OdpowiedźInterfejsu::Sukces(format!("Dodano budynek: {} z ID: {}", budynek.nazwa, id)),
                        Err(e) => OdpowiedźInterfejsu::Błąd(format!("Błąd dodawania budynku: {}", e)),
                    }
                },
            };
            
            if let Err(e) = nadajnik.send(odpowiedź).await {
                eprintln!("Błąd wysyłania odpowiedzi: {}", e);
            }
        }
    }
    
    pub async fn wyślij_komendę(&self, komenda: KomendaInterfejsu) -> Result<OdpowiedźInterfejsu, Box<dyn std::error::Error>> {
        self.nadajnik_komend.send(komenda).await
            .map_err(|e| Box::new(e) as Box<dyn std::error::Error>)?;
        
        match self.odbiornik_odpowiedzi.recv().await {
            Some(odpowiedź) => Ok(odpowiedź),
            None => Err(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Nie otrzymano odpowiedzi"))),
        }
    }
    
    pub fn sprawdź_stabilność_połączenia_kwantowego(&self) -> f64 {
        self.stan_połączenia_kwantowego
    }
    
    pub async fn monitoruj_stabilność_połączenia(&mut self) {
        // Symulacja monitorowania stabilności połączenia kwantowego
        // W rzeczywistej implementacji, moglibyśmy sprawdzać stan entanglacji
        // między różnymi urządzeniami i aktualizować stan_połączenia_kwantowego
        
        // Przykładowa implementacja:
        let menedżer_stanu_guard = self.menedżer_stanu.lock().unwrap();
        match menedżer_stanu_guard.pobierz_średni_stan_entanglacji().await {
            Ok(średnia) => {
                self.stan_połączenia_kwantowego = średnia;
                println!("Stabilność połączenia kwantowego: {:.2}", średnia);
                
                // Jeśli stabilność spadnie poniżej progu, automatycznie rekalibruj
                if średnia < 0.7 {
                    println!("Wykryto niską stabilność połączenia kwantowego. Rozpoczynam rekalibrację...");
                    self.rekalibruj_wszystkie_połączenia().await;
                }
            },
            Err(e) => {
                eprintln!("Błąd monitorowania stabilności: {}", e);
                // W przypadku błędu, zakładamy pewien spadek stabilności
                self.stan_połączenia_kwantowego *= 0.95;
            }
        }
    }
    
    async fn rekalibruj_wszystkie_połączenia(&self) {
        println!("Rekalibracja wszystkich połączeń kwantowych...");
        
        // Pobierz listę wszystkich urządzeń
        let menedżer_crm_guard = self.menedżer_crm.lock().unwrap();
        match menedżer_crm_guard.pobierz_wszystkie_urządzenia().await {
            Ok(urządzenia) => {
                for urządzenie in urządzenia {
                    match self.wyślij_komendę(KomendaInterfejsu::RekalibrujPołączenieKwantowe(urządzenie.id)).await {
                        Ok(_) => println!("Zrekalibrowano urządzenie ID: {}", urządzenie.id),
                        Err(e) => eprintln!("Błąd rekalibracji urządzenia ID: {}: {}", urządzenie.id, e),
                    }
                }
                println!("Rekalibracja zakończona.");
            },
            Err(e) => eprintln!("Błąd pobierania listy urządzeń: {}", e),
        }
    }
    
    pub async fn uruchom_interfejs(&mut self) {
        println!("Uruchamianie interfejsu użytkownika systemu HVAC CRM/ERP z elementami kwantowymi...");
        
        // Sprawdź początkową stabilność połączenia
        self.monitoruj_stabilność_połączenia().await;
        
        // Tutaj można zaimplementować pętlę główną interfejsu użytkownika
        // Na przykład, obsługę poleceń z konsoli, interfejsu graficznego, itp.
        
        println!("Interfejs użytkownika gotowy do pracy.");
        println!("Stabilność połączenia kwantowego: {:.2}", self.stan_połączenia_kwantowego);
    }
}

// Przykładowa implementacja funkcji main do testowania interfejsu
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Inicjalizacja komponentów
    let connection_string = "host=localhost dbname=hvac_crm_erp user=hvac_admin password=twoje_hasło";
    
    let menedżer_stanu = Arc::new(Mutex::new(MenedżerStanuKwantowego::nowy(connection_string).await?));
    let menedżer_crm = Arc::new(Mutex::new(MenedżerCRMERP::nowy(connection_string).await?));
    
    let integrator = Arc::new(IntegratorCRMKwantowy::nowy(
        menedżer_crm.clone(),
        menedżer_stanu.clone(),
    ));
    
    let interfejs_wizualizacji = Arc::new(Mutex::new(InterfejsWizualizacji::nowy()));
    
    // Utworzenie interfejsu użytkownika
    let mut interfejs = InterfejsUżytkownika::nowy(
        integrator.clone(),
        menedżer_crm.clone(),
        menedżer_stanu.clone(),
        interfejs_wizualizacji.clone(),
    );
    
    // Uruchomienie interfejsu
    interfejs.uruchom_interfejs().await;
    
    // Przykładowe użycie interfejsu
    let budynek = Budynek {
        id: 0, // ID zostanie nadane przez bazę danych
        nazwa: "Biurowiec Centrum".to_string(),
        adres: "ul. Kwantowa 123, 00-001 Warszawa".to_string(),
        współrzędne_gps: Some(vec![52.2297, 21.0122]),
        id_klienta: 1,
    };
    
    match interfejs.wyślij_komendę(KomendaInterfejsu::DodajBudynek(budynek)).await {
        Ok(odpowiedź) => println!("Otrzymano odpowiedź: {:?}", odpowiedź),
        Err(e) => eprintln!("Błąd: {}", e),
    }
    
    // Monitorowanie stabilności połączenia kwantowego
    for _ in 0..5 {
        tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
        interfejs.monitoruj_stabilność_połączenia().await;
    }
    
    Ok(())
}