use std::sync::{Arc, Mutex};
use tokio_postgres::{Client, NoTls, Error as PgError};
use serde::{Serialize, Deserialize};
use serde_json::Value as JsonValue;
use chrono::{DateTime, Utc};
use crate::stan_kwantowy_postgres::{MenedżerStanuKwantowego, StanKwantowyHVAC};

// Struktury danych dla modułu CRM/ERP

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Klient {
    pub id: i32,
    pub nazwa: String,
    pub email: Option<String>,
    pub telefon: Option<String>,
    pub adres: Option<String>,
    pub typ_klienta: Option<String>,
    pub data_rejestracji: DateTime<Utc>,
    pub ocena_zamożności: Option<f64>,
    pub ostatni_kontakt: Option<DateTime<Utc>>,
    pub notatki: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Budynek {
    pub id: i32,
    pub id_klienta: i32,
    pub nazwa: String,
    pub adres: String,
    pub współrzędne_geo: Option<(f64, f64)>, // (długość, szerokość)
    pub typ_budynku: Option<String>,
    pub powierzchnia: Option<f64>,
    pub liczba_pięter: Option<i32>,
    pub rok_budowy: Option<i32>,
    pub notatki: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UrządzenieHVAC {
    pub id: i32,
    pub id_budynku: i32,
    pub id_stanu_kwantowego: i32,
    pub model: String,
    pub numer_seryjny: Option<String>,
    pub data_instalacji: Option<DateTime<Utc>>,
    pub data_ostatniego_serwisu: Option<DateTime<Utc>>,
    pub status: String,
    pub lokalizacja_w_budynku: Option<String>,
    pub zdjęcie_url: Option<String>,
    pub dane_techniczne: Option<JsonValue>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Komunikacja {
    pub id: i32,
    pub id_klienta: i32,
    pub typ: String, // email, telefon, SMS
    pub kierunek: String, // przychodzący/wychodzący
    pub data_czas: DateTime<Utc>,
    pub treść: Option<String>,
    pub transkrypcja: Option<String>,
    pub kategoria: Option<String>,
    pub status: String,
    pub załączniki: Option<JsonValue>,
    pub analiza_sentymentu: Option<f64>,
    pub klasyfikacja: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Oferta {
    pub id: i32,
    pub id_klienta: i32,
    pub data_utworzenia: DateTime<Utc>,
    pub data_ważności: Option<DateTime<Utc>>,
    pub status: String,
    pub wartość_netto: f64,
    pub wartość_brutto: f64,
    pub waluta: String,
    pub treść: Option<String>,
    pub link_do_podpisu: Option<String>,
    pub data_podpisania: Option<DateTime<Utc>>,
    pub notatki: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ReakcjaOferty {
    pub id: i32,
    pub id_oferty: i32,
    pub typ_reakcji: String,
    pub data_czas: DateTime<Utc>,
    pub adres_ip: Option<String>,
    pub urządzenie: Option<String>,
    pub czas_spędzony: Option<i32>,
    pub notatki: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ZlecenieServisowe {
    pub id: i32,
    pub id_urządzenia: i32,
    pub id_klienta: i32,
    pub typ_zlecenia: String,
    pub priorytet: i32,
    pub status: String,
    pub data_utworzenia: DateTime<Utc>,
    pub data_planowana: Option<DateTime<Utc>>,
    pub data_realizacji: Option<DateTime<Utc>>,
    pub opis_problemu: Option<String>,
    pub rozwiązanie: Option<String>,
    pub koszt: Option<f64>,
    pub czas_realizacji: Option<i32>,
    pub notatki: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct StanSplątany {
    pub id: i32,
    pub id_urządzenia_1: i32,
    pub id_urządzenia_2: i32,
    pub stopień_splątania: f64,
    pub data_pomiaru: DateTime<Utc>,
    pub parametry_splątania: Option<JsonValue>,
    pub wpływ_na_wydajność: Option<String>,
    pub notatki: Option<String>,
}

// Menedżer CRM/ERP do obsługi bazy danych
pub struct MenedżerCRMERP {
    klient_db: Arc<Mutex<Client>>,
    menedżer_stanu_kwantowego: Arc<Mutex<MenedżerStanuKwantowego>>,
}

impl MenedżerCRMERP {
    pub async fn nowy(connection_string: &str, menedżer_stanu: Arc<Mutex<MenedżerStanuKwantowego>>) -> Result<Self, PgError> {
        let (klient, connection) = tokio_postgres::connect(connection_string, NoTls).await?;
        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("Błąd połączenia: {}", e);
            }
        });

        Ok(Self {
            klient_db: Arc::new(Mutex::new(klient)),
            menedżer_stanu_kwantowego: menedżer_stanu,
        })
    }

    // Metody dla klientów
    pub async fn dodaj_klienta(&self, klient: &Klient) -> Result<i32, PgError> {
        let query = "INSERT INTO klienci \
            (nazwa, email, telefon, adres, typ_klienta, data_rejestracji, ocena_zamożności, ostatni_kontakt, notatki) \
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) \
            RETURNING id";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &klient.nazwa,
                &klient.email,
                &klient.telefon,
                &klient.adres,
                &klient.typ_klienta,
                &klient.data_rejestracji,
                &klient.ocena_zamożności,
                &klient.ostatni_kontakt,
                &klient.notatki,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    pub async fn pobierz_klienta(&self, id: i32) -> Result<Klient, PgError> {
        let query = "SELECT id, nazwa, email, telefon, adres, typ_klienta, data_rejestracji, ocena_zamożności, ostatni_kontakt, notatki \
                     FROM klienci WHERE id = $1";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(query, &[&id]).await?;

        Ok(Klient {
            id: wiersz.get(0),
            nazwa: wiersz.get(1),
            email: wiersz.get(2),
            telefon: wiersz.get(3),
            adres: wiersz.get(4),
            typ_klienta: wiersz.get(5),
            data_rejestracji: wiersz.get(6),
            ocena_zamożności: wiersz.get(7),
            ostatni_kontakt: wiersz.get(8),
            notatki: wiersz.get(9),
        })
    }

    // Metody dla budynków
    pub async fn dodaj_budynek(&self, budynek: &Budynek) -> Result<i32, PgError> {
        let query = "INSERT INTO budynki \
            (id_klienta, nazwa, adres, współrzędne_geo, typ_budynku, powierzchnia, liczba_pięter, rok_budowy, notatki) \
            VALUES ($1, $2, $3, POINT($4, $5), $6, $7, $8, $9, $10) \
            RETURNING id"; // Assuming POINT constructor for coordinates

        let (lon, lat) = budynek.współrzędne_geo.unwrap_or((0.0, 0.0)); // Default or handle None better

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &budynek.id_klienta,
                &budynek.nazwa,
                &budynek.adres,
                &lon, // Longitude for POINT
                &lat, // Latitude for POINT
                &budynek.typ_budynku,
                &budynek.powierzchnia,
                &budynek.liczba_pięter,
                &budynek.rok_budowy,
                &budynek.notatki,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    pub async fn pobierz_dane_mapy_instalacji(&self, id_klienta: Option<i32>, region: Option<String>) -> Result<Vec<Budynek>, PgError> {
        let mut query = "SELECT id, id_klienta, nazwa, adres, współrzędne_geo[0] as lon, współrzędne_geo[1] as lat, typ_budynku, powierzchnia, liczba_pięter, rok_budowy, notatki FROM budynki WHERE 1=1".to_string(); // Assuming POINT can be accessed like an array
        let mut params: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = Vec::new();
        let mut param_index = 1;

        let id_klienta_val;
        if let Some(id) = id_klienta {
            id_klienta_val = id;
            query.push_str(&format!(" AND id_klienta = ${}", param_index));
            params.push(&id_klienta_val);
            param_index += 1;
        }

        let region_val;
        if let Some(ref reg) = region {
            region_val = format!("%{}%", reg);
            query.push_str(&format!(" AND adres ILIKE ${}", param_index)); // Use ILIKE for case-insensitive matching
            params.push(&region_val);
            // param_index += 1; // No need if last param
        }

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersze = klient_guard.query(&query, &params[..]).await?;

        let mut budynki = Vec::new();
        for wiersz in wiersze {
             let lon: Option<f64> = wiersz.get("lon");
             let lat: Option<f64> = wiersz.get("lat");
             let współrzędne = match (lon, lat) {
                 (Some(lo), Some(la)) => Some((lo, la)),
                 _ => None,
             };

            budynki.push(Budynek {
                id: wiersz.get("id"),
                id_klienta: wiersz.get("id_klienta"),
                nazwa: wiersz.get("nazwa"),
                adres: wiersz.get("adres"),
                współrzędne_geo: współrzędne,
                typ_budynku: wiersz.get("typ_budynku"),
                powierzchnia: wiersz.get("powierzchnia"),
                liczba_pięter: wiersz.get("liczba_pięter"),
                rok_budowy: wiersz.get("rok_budowy"),
                notatki: wiersz.get("notatki"),
            });
        }

        Ok(budynki)
    }

    // Metody dla urządzeń HVAC
    pub async fn dodaj_urządzenie(&self, urządzenie: &UrządzenieHVAC) -> Result<i32, PgError> {
        let query = "INSERT INTO urządzenia_hvac \
            (id_budynku, id_stanu_kwantowego, model, numer_seryjny, data_instalacji, data_ostatniego_serwisu, status, lokalizacja_w_budynku, zdjęcie_url, dane_techniczne) \
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) \
            RETURNING id";

        let dane_techniczne_json = match &urządzenie.dane_techniczne {
            Some(dane) => dane.clone(),
            None => serde_json::Value::Null,
        };

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &urządzenie.id_budynku,
                &urządzenie.id_stanu_kwantowego,
                &urządzenie.model,
                &urządzenie.numer_seryjny,
                &urządzenie.data_instalacji,
                &urządzenie.data_ostatniego_serwisu,
                &urządzenie.status,
                &urządzenie.lokalizacja_w_budynku,
                &urządzenie.zdjęcie_url,
                &dane_techniczne_json,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    // Metody dla stanów splątanych
    pub async fn zapisz_stan_splątany(&self, stan: &StanSplątany) -> Result<i32, PgError> {
        let query = "INSERT INTO stany_splątane \
            (id_urządzenia_1, id_urządzenia_2, stopień_splątania, data_pomiaru, parametry_splątania, wpływ_na_wydajność, notatki) \
            VALUES ($1, $2, $3, $4, $5, $6, $7) \
            RETURNING id";

        let parametry_json = match &stan.parametry_splątania {
            Some(parametry) => parametry.clone(),
            None => serde_json::Value::Null,
        };

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &stan.id_urządzenia_1,
                &stan.id_urządzenia_2,
                &stan.stopień_splątania,
                &stan.data_pomiaru,
                &parametry_json,
                &stan.wpływ_na_wydajność,
                &stan.notatki,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    pub async fn pobierz_stany_splątane_dla_urządzenia(&self, id_urządzenia: i32, min_stopień: f64) -> Result<Vec<StanSplątany>, PgError> {
        let query = "SELECT id, id_urządzenia_1, id_urządzenia_2, stopień_splątania, data_pomiaru, parametry_splątania, wpływ_na_wydajność, notatki \
                     FROM stany_splątane \
                     WHERE (id_urządzenia_1 = $1 OR id_urządzenia_2 = $1) AND stopień_splątania >= $2 \
                     ORDER BY stopień_splątania DESC";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersze = klient_guard.query(query, &[&id_urządzenia, &min_stopień]).await?;

        let mut stany = Vec::new();
        for wiersz in wiersze {
            stany.push(StanSplątany {
                id: wiersz.get(0),
                id_urządzenia_1: wiersz.get(1),
                id_urządzenia_2: wiersz.get(2),
                stopień_splątania: wiersz.get(3),
                data_pomiaru: wiersz.get(4),
                parametry_splątania: wiersz.get(5),
                wpływ_na_wydajność: wiersz.get(6),
                notatki: wiersz.get(7),
            });
        }

        Ok(stany)
    }

    // Metoda do analizy komunikacji z klientem
    pub async fn zapisz_komunikację(&self, komunikacja: &Komunikacja) -> Result<i32, PgError> {
        let query = "INSERT INTO komunikacja \
            (id_klienta, typ, kierunek, data_czas, treść, transkrypcja, kategoria, status, załączniki, analiza_sentymentu, klasyfikacja) \
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) \
            RETURNING id";

        let załączniki_json = match &komunikacja.załączniki {
            Some(załączniki) => załączniki.clone(),
            None => serde_json::Value::Null,
        };

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &komunikacja.id_klienta,
                &komunikacja.typ,
                &komunikacja.kierunek,
                &komunikacja.data_czas,
                &komunikacja.treść,
                &komunikacja.transkrypcja,
                &komunikacja.kategoria,
                &komunikacja.status,
                &załączniki_json,
                &komunikacja.analiza_sentymentu,
                &komunikacja.klasyfikacja,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    // Metoda do aktualizacji oceny zamożności klienta na podstawie analizy komunikacji
    pub async fn aktualizuj_ocenę_zamożności(&self, id_klienta: i32, nowa_ocena: f64) -> Result<(), PgError> {
        let query = "UPDATE klienci SET ocena_zamożności = $1 WHERE id = $2";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        klient_guard.execute(query, &[&nowa_ocena, &id_klienta]).await?;

        Ok(())
    }

    // Metoda do śledzenia reakcji na oferty
    pub async fn zapisz_reakcję_oferty(&self, reakcja: &ReakcjaOferty) -> Result<i32, PgError> {
        let query = "INSERT INTO reakcje_oferty \
            (id_oferty, typ_reakcji, data_czas, adres_ip, urządzenie, czas_spędzony, notatki) \
            VALUES ($1, $2, $3, $4, $5, $6, $7) \
            RETURNING id";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let wiersz = klient_guard.query_one(
            query,
            &[
                &reakcja.id_oferty,
                &reakcja.typ_reakcji,
                &reakcja.data_czas,
                &reakcja.adres_ip,
                &reakcja.urządzenie,
                &reakcja.czas_spędzony,
                &reakcja.notatki,
            ],
        ).await?;

        Ok(wiersz.get(0))
    }

    // Metoda integrująca stan kwantowy z urządzeniem HVAC
    pub async fn powiąż_stan_kwantowy_z_urządzeniem(&self, id_urządzenia: i32, id_stanu: i32) -> Result<(), PgError> {
        // Najpierw sprawdzamy, czy stan kwantowy istnieje
        let menedżer_lock_result = self.menedżer_stanu_kwantowego.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        
        // Próba pobrania stanu kwantowego
        let _stan = menedżer_lock_result.pobierz_stan(id_stanu).await?;
        drop(menedżer_lock_result); // Zwalniamy blokadę

        // Aktualizujemy urządzenie, aby wskazywało na stan kwantowy
        let query = "UPDATE urządzenia_hvac SET id_stanu_kwantowego = $1 WHERE id = $2";
        let klient_guard = self.klient_db.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        klient_guard.execute(query, &[&id_stanu, &id_urządzenia]).await?;

        Ok(())
    }

    // Metoda do obliczania i zapisywania stopnia splątania między urządzeniami
    pub async fn oblicz_i_zapisz_splątanie(&self, id_urządzenia_1: i32, id_urządzenia_2: i32) -> Result<f64, PgError> {
        // Pobieramy stany kwantowe obu urządzeń
        let query_urządzenia = "SELECT id_stanu_kwantowego FROM urządzenia_hvac WHERE id = $1";
        let klient_guard = self.klient_db.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        
        let wiersz_1 = klient_guard.query_one(query_urządzenia, &[&id_urządzenia_1]).await?;
        let id_stanu_1: i32 = wiersz_1.get(0);
        
        let wiersz_2 = klient_guard.query_one(query_urządzenia, &[&id_urządzenia_2]).await?;
        let id_stanu_2: i32 = wiersz_2.get(0);
        
        drop(klient_guard); // Zwalniamy blokadę klienta DB

        // Pobieramy stany kwantowe
        let menedżer_lock_result = self.menedżer_stanu_kwantowego.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        
        let stan_1_arc = menedżer_lock_result.pobierz_stan(id_stanu_1).await?;
        let stan_2_arc = menedżer_lock_result.pobierz_stan(id_stanu_2).await?;
        
        // Obliczamy stopień splątania (uproszczona implementacja)
        let stan_1 = stan_1_arc.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        let stan_2 = stan_2_arc.lock().map_err(|_| 
            PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;
        
        // Przykładowa implementacja obliczania stopnia splątania
        // W rzeczywistości byłaby to bardziej złożona funkcja kwantowa
        let mut stopień_splątania = 0.0;
        
        // Porównujemy stany entanglacji obu urządzeń
        if !stan_1.stan_entanglacji.is_empty() && !stan_2.stan_entanglacji.is_empty() {
            // Przykładowe obliczenie - średnia korelacja między stanami entanglacji
            let min_len = std::cmp::min(stan_1.stan_entanglacji.len(), stan_2.stan_entanglacji.len());
            let mut suma_korelacji = 0.0;
            
            for i in 0..min_len {
                suma_korelacji += (stan_1.stan_entanglacji[i] * stan_2.stan_entanglacji[i]).abs();
            }
            
            stopień_splątania = suma_korelacji / min_len as f64;
        }
        
        drop(stan_1);
        drop(stan_2);
        drop(menedżer_lock_result);
        
        // Zapisujemy wynik splątania do bazy danych
        let stan_splątany = StanSplątany {
            id: 0, // ID zostanie przypisane przez bazę danych
            id_urządzenia_1,
            id_urządzenia_2,
            stopień_splątania,
            data_pomiaru: Utc::now(),
            parametry_splątania: None,
            wpływ_na_wydajność: None,
            notatki: Some(format!("Automatyczny pomiar splątania między urządzeniami {} i {}", id_urządzenia_1, id_urządzenia_2)),
        };
        
        let _id = self.zapisz_stan_splątany(&stan_splątany).await?;
        
        Ok(stopień_splątania)
    }

    pub async fn pobierz_dane_dashboardu(&self) -> Result<(i64, i64, f64, i64), PgError> {
        let query_klienci = "SELECT COUNT(*) FROM klienci";
        let query_urządzenia = "SELECT COUNT(*) FROM urządzenia_hvac";
        let query_zlecenia = "SELECT COUNT(*) FROM zlecenia_serwisowe WHERE status = 'aktywne'";

        let klient_guard = self.klient_db.lock().map_err(|_| PgError::from_source(Box::new(std::io::Error::new(std::io::ErrorKind::Other, "Mutex lock failed"))))?;

        let wiersz_klienci = klient_guard.query_one(query_klienci, &[]).await?;
        let liczba_klientów: i64 = wiersz_klienci.get(0);

        let wiersz_urządzenia = klient_guard.query_one(query_urządzenia, &[]).await?;
        let liczba_urządzeń: i64 = wiersz_urządzenia.get(0);

        let wiersz_zlecenia = klient_guard.query_one(query_zlecenia, &[]).await?;
        let liczba_zleceń: i64 = wiersz_zlecenia.get(0);

        // Pobierz średnią stabilność połączenia kwantowego
        let średnia_stabilność = self.menedżer_stanu_kwantowego.lock().unwrap().pobierz_średni_stan_entanglacji().await?;

        Ok((liczba_klientów, liczba_urządzeń, średnia_stabilność, liczba_zleceń))
    }
}
