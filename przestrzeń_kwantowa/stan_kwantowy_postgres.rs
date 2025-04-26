use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio_postgres::{Client, NoTls, Error as PgError};
use serde::{Serialize, Deserialize};
use serde_json::Value as JsonValue;

#[derive(Debug, Serialize, Deserialize)]
pub struct StanKwantowyHVAC {
    id: i32,
    temperatura: f64,
    wilgotność: f64,
    ciśnienie: f64,
    przepływ_powietrza: f64,
    stan_entanglacji: Vec<f64>,
    parametry_crm: ParametryCRM,
}

#[derive(Debug, Serialize, Deserialize, Clone)] // Dodano Clone
struct ParametryCRM {
    id_klienta: i32,
    priorytet_serwisu: i32,
    historia_serwisowa: Vec<DaneHistoryczne>,
    predykcje_awarii: Vec<PredykcjaAwarii>,
    odczyty_sensorow_kwantowych: Vec<f64>, // Nowe pole
}

#[derive(Debug, Serialize, Deserialize)]
struct DaneHistoryczne {
    timestamp: i64,
    typ_serwisu: String,
    parametry_systemu: Vec<f64>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PredykcjaAwarii {
    komponent: String,
    prawdopodobieństwo: f64,
    estymowany_czas: i64,
}

pub struct MenedżerStanuKwantowego {
    klient_db: Arc<Mutex<Client>>,
    cache_stanów: HashMap<i32, Arc<Mutex<StanKwantowyHVAC>>>,
}

impl MenedżerStanuKwantowego {
    pub async fn nowy(connection_string: &str) -> Result<Self, PgError> {
        let (klient, connection) = tokio_postgres::connect(connection_string, NoTls).await?;
        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("Błąd połączenia: {}", e);
            }
        });

        Ok(Self {
            klient_db: Arc::new(Mutex::new(klient)),
            cache_stanów: HashMap::new(),
        })
    }

    pub async fn zapisz_stan(&mut self, stan: StanKwantowyHVAC) -> Result<(), PgError> {
        let query = "INSERT INTO stany_kwantowe_hvac \
            (id, temperatura, wilgotność, ciśnienie, przepływ_powietrza, stan_entanglacji, parametry_crm) \
            VALUES ($1, $2, $3, $4, $5, $6, $7) \
            ON CONFLICT (id) DO UPDATE SET \
            temperatura = EXCLUDED.temperatura, \
            wilgotność = EXCLUDED.wilgotność, \
            ciśnienie = EXCLUDED.ciśnienie, \
            przepływ_powietrza = EXCLUDED.przepływ_powietrza, \
            stan_entanglacji = EXCLUDED.stan_entanglacji, \
            parametry_crm = EXCLUDED.parametry_crm";

        let parametry_json = serde_json::to_value(&stan.parametry_crm)
            .map_err(|e| PgError::from_source(Box::new(e)))?; // Lepsza obsługa błędów

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        klient_guard.execute(
            query,
            &[
                &stan.id,
                &stan.temperatura,
                &stan.wilgotność,
                &stan.ciśnienie,
                &stan.przepływ_powietrza,
                &stan.stan_entanglacji,
                &parametry_json,
            ],
        ).await?;

        // Aktualizacja cache - używamy clone(), aby uniknąć przeniesienia własności
        if let Some(cached_stan_arc) = self.cache_stanów.get_mut(&stan.id) {
            let mut cached_stan = cached_stan_arc.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
            *cached_stan = stan.clone(); // Klonujemy nowy stan do cache
        } else {
            self.cache_stanów.insert(stan.id, Arc::new(Mutex::new(stan)));
        }

        Ok(())
    }

    pub async fn pobierz_stan(&mut self, id: i32) -> Result<Arc<Mutex<StanKwantowyHVAC>>, PgError> { // Zmieniono na &mut self
        if let Some(stan) = self.cache_stanów.get(&id) {
            return Ok(Arc::clone(stan));
        }

        let query = "SELECT id, temperatura, wilgotność, ciśnienie, przepływ_powietrza, stan_entanglacji, parametry_crm FROM stany_kwantowe_hvac WHERE id = $1";
        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(query, &[&id]).await?;

        let parametry_crm_json: JsonValue = wiersz.get(6);
        let stan = StanKwantowyHVAC {
            id: wiersz.get(0),
            temperatura: wiersz.get(1),
            wilgotność: wiersz.get(2),
            ciśnienie: wiersz.get(3),
            przepływ_powietrza: wiersz.get(4),
            stan_entanglacji: wiersz.get(5),
            parametry_crm: serde_json::from_value(parametry_crm_json)
                .map_err(|e| PgError::from_source(Box::new(e)))?,
        };

        let stan_arc = Arc::new(Mutex::new(stan));
        // Dodajemy do cache - wymaga &mut self
        self.cache_stanów.insert(id, Arc::clone(&stan_arc));
        Ok(stan_arc)
    }

    pub async fn aktualizuj_predykcje(&mut self, id: i32, predykcje: Vec<PredykcjaAwarii>) -> Result<(), PgError> {
        if let Some(stan_arc) = self.cache_stanów.get(&id) {
            if let Ok(mut stan) = stan_arc.lock() {
                stan.parametry_crm.predykcje_awarii = predykcje.clone();
                
                let query = "UPDATE stany_kwantowe_hvac SET parametry_crm = $1 WHERE id = $2";
                let parametry_json = serde_json::to_value(&stan.parametry_crm)
                    .map_err(|e| PgError::new(e.to_string()))?;

                if let Ok(klient) = self.klient_db.lock() {
                    klient.execute(query, &[&parametry_json, &id]).await?;
                }
            }
        }

        Ok(())
    }

    // Nowa funkcja do odpytywania stanów na podstawie kryteriów splątania
    pub async fn pobierz_stany_po_entanglacji(&self, prog_entanglacji: f64) -> Result<Vec<StanKwantowyHVAC>, PgError> {
        // Przykład zapytania - wymaga dostosowania do faktycznej struktury danych `stan_entanglacji`
        // Zakładamy, że `stan_entanglacji` to Vec<f64> i chcemy znaleźć stany, gdzie np. pierwszy element > prog_entanglacji
        // W PostgreSQL można użyć operatorów JSONB lub przechowywać splątanie w bardziej strukturalny sposób.
        // Poniższe zapytanie jest uproszczone i może wymagać modyfikacji.
        let query = "SELECT id, temperatura, wilgotność, ciśnienie, przepływ_powietrza, stan_entanglacji, parametry_crm 
                     FROM stany_kwantowe_hvac 
                     WHERE CAST(stan_entanglacji ->> 0 AS FLOAT) > $1"; // Przykład - dostosuj do schematu!

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersze = klient_guard.query(query, &[&prog_entanglacji]).await?;

        let mut wyniki = Vec::new();
        for wiersz in wiersze {
            let parametry_crm_json: JsonValue = wiersz.get(6);
            let stan = StanKwantowyHVAC {
                id: wiersz.get(0),
                temperatura: wiersz.get(1),
                wilgotność: wiersz.get(2),
                ciśnienie: wiersz.get(3),
                przepływ_powietrza: wiersz.get(4),
                stan_entanglacji: wiersz.get(5),
                parametry_crm: serde_json::from_value(parametry_crm_json)
                    .map_err(|e| PgError::from_source(Box::new(e)))?,
            };
            wyniki.push(stan);
        }

        Ok(wyniki)
    }
}