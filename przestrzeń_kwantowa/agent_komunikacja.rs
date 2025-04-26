use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::sync::mpsc::{channel, Sender, Receiver};
use serde::{Serialize, Deserialize};
use crate::stan_kwantowy_postgres::{StanKwantowyHVAC, PredykcjaAwarii, MenedżerStanuKwantowego}; // Added MenedżerStanuKwantowego import

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum KomunikatAgenta {
    AktualizacjaStanu(StanKwantowyHVAC),
    ŻądanieStanu(i32),
    PredykcjaAwarii {
        id_systemu: i32,
        komponenty: Vec<String>,
    },
    OptymalizacjaParametrów {
        id_systemu: i32,
        parametry: HashMap<String, f64>,
    },
    ŻądanieStanówSplątanych { prog_entanglacji: f64 }, // Nowy wariant
}

pub struct AgentHVAC {
    id: String,
    nadawca: Sender<KomunikatAgenta>,
    odbiornik: Receiver<KomunikatAgenta>,
    stan_kwantowy: Arc<Mutex<StanKwantowyHVAC>>,
    agenci_połączeni: HashMap<String, Sender<KomunikatAgenta>>,
    menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>, // Added state manager
}

impl AgentHVAC {
    pub async fn nowy(id: String, początkowy_stan: StanKwantowyHVAC, menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>) -> Self {
        let (tx, rx) = channel(100);
        
        Self {
            id,
            nadawca: tx,
            odbiornik: rx,
            stan_kwantowy: Arc::new(Mutex::new(początkowy_stan)),
            agenci_połączeni: HashMap::new(),
            menedżer_stanu, // Store the state manager
        }
    }

    pub async fn połącz_z_agentem(&mut self, id_agenta: String, nadawca: Sender<KomunikatAgenta>) {
        self.agenci_połączeni.insert(id_agenta, nadawca);
    }

    pub async fn rozpocznij_nasłuchiwanie(&mut self) {
        while let Some(komunikat) = self.odbiornik.recv().await {
            self.przetwórz_komunikat(komunikat).await;
        }
    }

    async fn przetwórz_komunikat(&mut self, komunikat: KomunikatAgenta) {
        match komunikat {
            KomunikatAgenta::AktualizacjaStanu(nowy_stan) => {
                let stan_do_zapisu = nowy_stan.clone(); // Clone before locking
                if let Ok(mut stan) = self.stan_kwantowy.lock() {
                    *stan = nowy_stan;
                    // Persist state change to DB
                    let menedżer_lock_result = self.menedżer_stanu.lock();
                    if let Ok(mut menedżer) = menedżer_lock_result {
                        if let Err(e) = menedżer.zapisz_stan(stan_do_zapisu).await {
                            eprintln!("Agent {} BŁĄD: Nie udało się zapisać stanu po aktualizacji: {}", self.id, e);
                        }
                    } else {
                        eprintln!("Agent {} BŁĄD: Nie udało się uzyskać blokady menedżera stanu do zapisu stanu.", self.id);
                    }
                    drop(stan); // Release lock before propagating
                    self.propaguj_aktualizację().await;
                }
            },
            KomunikatAgenta::ŻądanieStanu(id) => {
                if let Ok(stan) = self.stan_kwantowy.lock() {
                    if stan.id == id {
                        self.wyślij_stan_do_wszystkich(stan.clone()).await;
                    }
                }
            },
            KomunikatAgenta::PredykcjaAwarii { id_systemu, komponenty } => {
                // Ensure this agent is responsible for the given system ID
                if let Ok(stan) = self.stan_kwantowy.lock() {
                    if stan.id == id_systemu {
                        drop(stan); // Release lock before async call
                        self.analizuj_predykcje(komponenty).await;
                    } else {
                        // Optionally forward the request or log an error
                        eprintln!("Agent {} received prediction request for wrong system ID {}", self.id, id_systemu);
                    }
                } else {
                     eprintln!("Agent {} failed to lock state for prediction analysis", self.id);
                }
            },
            KomunikatAgenta::OptymalizacjaParametrów { id_systemu, parametry } => {
                 // Ensure this agent is responsible for the given system ID
                if let Ok(mut stan) = self.stan_kwantowy.lock() {
                     if stan.id == id_systemu {
                        // Implementacja optymalizacji parametrów systemu HVAC
                        stan.temperatura = *parametry.get("temperatura").unwrap_or(&stan.temperatura);
                        stan.wilgotność = *parametry.get("wilgotność").unwrap_or(&stan.wilgotność);
                        stan.przepływ_powietrza = *parametry.get("przepływ").unwrap_or(&stan.przepływ_powietrza);
                        
                        let stan_do_zapisu = stan.clone(); // Clone before releasing lock
                        drop(stan); // Release lock before async call

                        // Persist state change to DB
                        let menedżer_lock_result = self.menedżer_stanu.lock();
                        if let Ok(mut menedżer) = menedżer_lock_result {
                            if let Err(e) = menedżer.zapisz_stan(stan_do_zapisu).await {
                                eprintln!("Agent {} BŁĄD: Nie udało się zapisać zoptymalizowanego stanu: {}", self.id, e);
                            }
                        } else {
                            eprintln!("Agent {} BŁĄD: Nie udało się uzyskać blokady menedżera stanu do zapisu zoptymalizowanego stanu.", self.id);
                        }

                        self.propaguj_aktualizację().await;
                    } else {
                        // Optionally forward the request or log an error
                        eprintln!("Agent {} received optimization request for wrong system ID {}", self.id, id_systemu);
                    }
                } else {
                    eprintln!("Agent {} failed to lock state for optimization", self.id);
                }
            },
            KomunikatAgenta::ŻądanieStanówSplątanych { prog_entanglacji } => {
                println!("Agent {} otrzymał żądanie stanów splątanych z progiem: {}", self.id, prog_entanglacji);
                let menedżer_lock_result = self.menedżer_stanu.lock();
                if let Ok(menedżer) = menedżer_lock_result { // Nie potrzebujemy mut, bo pobierz_stany_po_entanglacji wymaga &self
                    match menedżer.pobierz_stany_po_entanglacji(prog_entanglacji).await {
                        Ok(stany) => {
                            println!("Agent {} pomyślnie pobrał {} stanów splątanych.", self.id, stany.len());
                            // TODO: Zdecydować co zrobić z pobranymi stanami (np. wysłać do innego agenta, przetworzyć lokalnie)
                            // Na razie tylko logujemy
                            for stan in stany {
                                println!("  - Stan ID: {}", stan.id); // Zakładając, że StanKwantowyHVAC ma publiczne pole id lub metodę get_id()
                            }
                        },
                        Err(e) => {
                            eprintln!("Agent {} BŁĄD: Nie udało się pobrać stanów splątanych: {}", self.id, e);
                        }
                    }
                } else {
                    eprintln!("Agent {} BŁĄD: Nie udało się uzyskać blokady menedżera stanu do pobrania stanów splątanych.", self.id);
                }
            }
        }
    }

    async fn propaguj_aktualizację(&self) {
        if let Ok(stan) = self.stan_kwantowy.lock() {
            let komunikat = KomunikatAgenta::AktualizacjaStanu(stan.clone());
            for nadawca in self.agenci_połączeni.values() {
                let _ = nadawca.send(komunikat.clone()).await;
            }
        }
    }

    async fn wyślij_stan_do_wszystkich(&self, stan: StanKwantowyHVAC) {
        let komunikat = KomunikatAgenta::AktualizacjaStanu(stan);
        for nadawca in self.agenci_połączeni.values() {
            let _ = nadawca.send(komunikat.clone()).await;
        }
    }

    async fn analizuj_predykcje(&self, komponenty: Vec<String>) { // Removed id_systemu as it's checked in caller
        // Implementacja analizy predykcyjnej dla komponentów HVAC
        let predykcje = komponenty.iter().map(|komponent| {
            PredykcjaAwarii {
                komponent: komponent.clone(),
                prawdopodobieństwo: self.oblicz_prawdopodobieństwo_awarii(komponent),
                estymowany_czas: chrono::Utc::now().timestamp() + 86400, // 24h
            }
        }).collect::<Vec<_>>(); // Explicit type annotation

        let system_id_for_update;
        if let Ok(mut stan) = self.stan_kwantowy.lock() {
            system_id_for_update = stan.id;
            stan.parametry_crm.predykcje_awarii = predykcje.clone(); // Clone predictions for update
            println!("Agent {} updated local predictions for system {}", self.id, stan.id);
            drop(stan); // Release lock before DB call

            // Update predictions in DB
            let menedżer_lock_result = self.menedżer_stanu.lock();
            if let Ok(mut menedżer) = menedżer_lock_result {
                 if let Err(e) = menedżer.aktualizuj_predykcje(system_id_for_update, predykcje).await {
                     eprintln!("Agent {} BŁĄD: Nie udało się zaktualizować predykcji w DB dla systemu {}: {}", self.id, system_id_for_update, e);
                 }
            } else {
                 eprintln!("Agent {} BŁĄD: Nie udało się uzyskać blokady menedżera stanu do aktualizacji predykcji.", self.id);
            }
        } else {
            eprintln!("Agent {} failed to lock state for prediction analysis", self.id);
        }
    }

    fn oblicz_prawdopodobieństwo_awarii(&self, komponent: &str) -> f64 {
        // Implementacja modelu predykcyjnego dla komponentów HVAC
        // TODO: Dodać zaawansowany model ML
        0.5 // Przykładowa wartość
    }

    // Removed optymalizuj_system as logic moved to przetwórz_komunikat
}