use std::sync::{Arc, Mutex};
use tokio::sync::mpsc::{Sender};
use serde::{Serialize, Deserialize};
use chrono::Utc;
use crate::stan_kwantowy_postgres::{MenedżerStanuKwantowego, StanKwantowyHVAC};
use crate::crm_erp_postgres::{MenedżerCRMERP, Komunikacja, Klient, UrządzenieHVAC, StanSplątany};
use crate::agent_komunikacja::{AgentHVAC, KomunikatAgenta};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum KomunikatCRM {
    NowaKomunikacja(Komunikacja),
    NowyKlient(Klient),
    NoweUrządzenie(UrządzenieHVAC),
    AktualizacjaZamożności {
        id_klienta: i32,
        nowa_ocena: f64,
    },
    ŻądanieAnalizyTranskrypcji {
        id_komunikacji: i32,
        transkrypcja: String,
    },
    ŻądanieObliczeniaSplątania {
        id_urządzenia_1: i32,
        id_urządzenia_2: i32,
    },
    ŻądanieMapyInstalacji {
        id_klienta: Option<i32>,
        region: Option<String>,
    },
}

pub struct IntegratorCRMKwantowy {
    menedżer_crm: Arc<Mutex<MenedżerCRMERP>>,
    menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>,
    agenci: Vec<Arc<Mutex<AgentHVAC>>>,
}

impl IntegratorCRMKwantowy {
    pub fn nowy(
        menedżer_crm: Arc<Mutex<MenedżerCRMERP>>,
        menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>,
    ) -> Self {
        Self {
            menedżer_crm,
            menedżer_stanu,
            agenci: Vec::new(),
        }
    }

    pub fn dodaj_agenta(&mut self, agent: Arc<Mutex<AgentHVAC>>) {
        self.agenci.push(agent);
    }

    pub async fn przetwórz_komunikat_crm(&self, komunikat: KomunikatCRM) -> Result<(), Box<dyn std::error::Error>> {
        match komunikat {
            KomunikatCRM::NowaKomunikacja(komunikacja) => {
                // Zapisz komunikację w bazie danych
                let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
                let id_komunikacji = menedżer_crm.zapisz_komunikację(&komunikacja).await?;
                drop(menedżer_crm);
                
                println!("Zapisano nową komunikację o ID: {}", id_komunikacji);
                
                // Jeśli to transkrypcja, możemy przeprowadzić analizę zamożności
                if komunikacja.typ == "telefon" && komunikacja.transkrypcja.is_some() {
                    self.analizuj_transkrypcję(id_komunikacji, komunikacja.id_klienta, komunikacja.transkrypcja.unwrap()).await?;
                }
            },
            KomunikatCRM::NowyKlient(klient) => {
                let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
                let id_klienta = menedżer_crm.dodaj_klienta(&klient).await?;
                println!("Dodano nowego klienta o ID: {}", id_klienta);
            },
            KomunikatCRM::NoweUrządzenie(urządzenie) => {
                // Dodaj urządzenie i powiąż je ze stanem kwantowym
                let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
                let id_urządzenia = menedżer_crm.dodaj_urządzenie(&urządzenie).await?;
                
                // Powiąż urządzenie ze stanem kwantowym
                menedżer_crm.powiąż_stan_kwantowy_z_urządzeniem(id_urządzenia, urządzenie.id_stanu_kwantowego).await?;
                println!("Dodano nowe urządzenie o ID: {} i powiązano ze stanem kwantowym ID: {}", id_urządzenia, urządzenie.id_stanu_kwantowego);
                
                // Sprawdź splątanie z innymi urządzeniami
                self.sprawdź_splątanie_z_innymi_urządzeniami(id_urządzenia).await?;
            },
            KomunikatCRM::AktualizacjaZamożności { id_klienta, nowa_ocena } => {
                let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
                menedżer_crm.aktualizuj_ocenę_zamożności(id_klienta, nowa_ocena).await?;
                println!("Zaktualizowano ocenę zamożności klienta ID: {} na wartość: {}", id_klienta, nowa_ocena);
            },
            KomunikatCRM::ŻądanieAnalizyTranskrypcji { id_komunikacji, transkrypcja } => {
                // Pobierz komunikację, aby uzyskać ID klienta
                // W tym przykładzie zakładamy, że znamy ID klienta (w praktyce trzeba by pobrać z bazy)
                let id_klienta = 1; // Przykładowe ID
                self.analizuj_transkrypcję(id_komunikacji, id_klienta, transkrypcja).await?;
            },
            KomunikatCRM::ŻądanieObliczeniaSplątania { id_urządzenia_1, id_urządzenia_2 } => {
                let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
                let stopień_splątania = menedżer_crm.oblicz_i_zapisz_splątanie(id_urządzenia_1, id_urządzenia_2).await?;
                println!("Obliczono stopień splątania między urządzeniami {} i {}: {}", id_urządzenia_1, id_urządzenia_2, stopień_splątania);
                
                // Jeśli stopień splątania jest wysoki, powiadom agentów
                if stopień_splątania > 0.7 {
                    self.powiadom_agentów_o_splątaniu(id_urządzenia_1, id_urządzenia_2, stopień_splątania).await?;
                }
            },
            KomunikatCRM::ŻądanieMapyInstalacji { id_klienta, region } => {
                println!("Generowanie mapy instalacji dla klienta ID: {:?}, region: {:?}", id_klienta, region);
                // Tutaj byłaby implementacja generowania mapy instalacji
                // Wymagałoby to integracji z biblioteką do wizualizacji geograficznej
            },
        }
        
        Ok(())
    }
    
    async fn analizuj_transkrypcję(&self, id_komunikacji: i32, id_klienta: i32, transkrypcja: String) -> Result<(), Box<dyn std::error::Error>> {
        println!("Analizowanie transkrypcji dla komunikacji ID: {}, klienta ID: {}", id_komunikacji, id_klienta);
        
        // Tutaj byłaby implementacja analizy transkrypcji za pomocą modelu ML
        // W tym przykładzie używamy prostego algorytmu
        
        // Przykładowe słowa kluczowe wskazujące na zamożność
        let słowa_zamożności = vec!["luksusowy", "premium", "inwestycja", "rezydencja", "jacht", "prywatny"];
        
        // Prosta analiza - liczymy wystąpienia słów kluczowych
        let transkrypcja_lower = transkrypcja.to_lowercase();
        let mut liczba_trafień = 0;
        
        for słowo in słowa_zamożności {
            if transkrypcja_lower.contains(słowo) {
                liczba_trafień += 1;
            }
        }
        
        // Obliczamy ocenę zamożności (0.0 - 1.0)
        let ocena_zamożności = (liczba_trafień as f64) / (słowa_zamożności.len() as f64);
        
        // Aktualizujemy ocenę zamożności klienta
        let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
        menedżer_crm.aktualizuj_ocenę_zamożności(id_klienta, ocena_zamożności).await?;
        
        println!("Zaktualizowano ocenę zamożności klienta ID: {} na wartość: {}", id_klienta, ocena_zamożności);
        
        Ok(())
    }
    
    async fn sprawdź_splątanie_z_innymi_urządzeniami(&self, id_urządzenia: i32) -> Result<(), Box<dyn std::error::Error>> {
        // Pobierz listę wszystkich urządzeń (w praktyce należałoby filtrować, np. po lokalizacji)
        // W tym przykładzie zakładamy, że mamy listę ID urządzeń do sprawdzenia
        let urządzenia_do_sprawdzenia = vec![1, 2, 3, 4, 5]; // Przykładowe ID
        
        let menedżer_crm = self.menedżer_crm.lock().map_err(|e| format!("Błąd blokady: {}", e))?;
        
        for &inne_id in &urządzenia_do_sprawdzenia {
            if inne_id != id_urządzenia {
                match menedżer_crm.oblicz_i_zapisz_splątanie(id_urządzenia, inne_id).await {
                    Ok(stopień) => {
                        println!("Obliczono stopień splątania między urządzeniami {} i {}: {}", id_urządzenia, inne_id, stopień);
                        
                        // Jeśli stopień splątania jest wysoki, powiadom agentów
                        if stopień > 0.7 {
                            drop(menedżer_crm); // Zwalniamy blokadę przed wywołaniem innej metody
                            self.powiadom_agentów_o_splątaniu(id_urządzenia, inne_id, stopień).await?;
                            return Ok(()); // Kończymy po znalezieniu pierwszego silnego splątania
                        }
                    },
                    Err(e) => {
                        eprintln!("Błąd podczas obliczania splątania: {}", e);
                    }
                }
            }
        }
        
        Ok(())
    }
    
    async fn powiadom_agentów_o_splątaniu(&self, id_urządzenia_1: i32, id_urządzenia_2: i32, stopień_splątania: f64) -> Result<(), Box<dyn std::error::Error>> {
        // Tworzymy komunikat o wysokim stopniu splątania
        let komunikat = KomunikatAgenta::ŻądanieStanówSplątanych { prog_entanglacji: stopień_splątania };
        
        // Wysyłamy komunikat do wszystkich agentów
        for agent_arc in &self.agenci {
            if let Ok(agent) = agent_arc.lock() {
                // Zakładamy, że AgentHVAC ma metodę do uzyskania nadawcy
                // W rzeczywistości trzeba by zmodyfikować AgentHVAC, aby udostępniał nadawcę
                // lub zaimplementować inny mechanizm komunikacji
                println!("Powiadamianie agenta {} o wysokim stopniu splątania: {}", agent.id, stopień_splątania);
                
                // Tutaj byłoby wysłanie komunikatu do agenta
                // agent.nadawca.send(komunikat.clone()).await?;
            }
        }
        
        Ok(())
    }
}