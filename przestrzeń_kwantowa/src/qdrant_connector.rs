use std::env;
use qdrant_client::prelude::*;
use tokio::time::{sleep, Duration};

pub async fn verify_qdrant_connection() -> Result<(), String> {
    let endpoint = env::var("QDRANT_ENDPOINT")
        .map_err(|_| "Brak zmiennej QDRANT_ENDPOINT".to_string())?;
    let api_key = env::var("QDRANT_API_KEY")
        .map_err(|_| "Brak zmiennej QDRANT_API_KEY".to_string())?;

    let client = QdrantClient::new(
        qdrant_client::client::QdrantClientConfig::from_url(&endpoint)
            .with_api_key(api_key)
    )?;

    let max_retries = env::var("QUANTUM_RETRY_ATTEMPTS")
        .unwrap_or("3".to_string())
        .parse::<u32>()
        .unwrap_or(3);

    for attempt in 0..max_retries {
        match client.list_collections().await {
            Ok(_) => return Ok(()),
            Err(e) => {
                if attempt == max_retries - 1 {
                    return Err(format!("Połączenie nieudane po {} próbach: {}", max_retries, e));
                }
                sleep(Duration::from_secs(2u64.pow(attempt))).await;
            }
        }
    }
    Err("Nieznany błąd połączenia".to_string())
}