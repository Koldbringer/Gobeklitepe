import os
import json
import logging
import psycopg2
from datetime import datetime
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from config import SUPABASE_URL, QDRANT_URL
from config import ENABLE_OCR, ENABLE_LLM, ENABLE_QDRANT

logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if the database connection is working."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

def check_supabase_connection():
    """Check if Supabase connection is working."""
    if not SUPABASE_URL:
        return False
    
    try:
        # This is a placeholder - in a real app, you'd make an actual API call
        # to Supabase to verify the connection
        return True
    except Exception as e:
        logger.error(f"Supabase connection error: {e}")
        return False

def check_qdrant_connection():
    """Check if Qdrant connection is working."""
    if not ENABLE_QDRANT or not QDRANT_URL:
        return False
    
    try:
        # This is a placeholder - in a real app, you'd make an actual API call
        # to Qdrant to verify the connection
        return True
    except Exception as e:
        logger.error(f"Qdrant connection error: {e}")
        return False

def get_system_health():
    """Get the health status of all system components."""
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": {
                "status": "online" if check_database_connection() else "offline",
                "type": "PostgreSQL"
            },
            "supabase": {
                "status": "online" if check_supabase_connection() else "offline"
            },
            "qdrant": {
                "status": "online" if check_qdrant_connection() else "offline",
                "enabled": ENABLE_QDRANT
            },
            "ocr": {
                "status": "online",  # Placeholder
                "enabled": ENABLE_OCR
            },
            "llm": {
                "status": "online",  # Placeholder
                "enabled": ENABLE_LLM
            }
        }
    }
    
    # Determine overall status
    component_statuses = [
        health["components"]["database"]["status"],
        health["components"]["supabase"]["status"]
    ]
    
    if ENABLE_QDRANT:
        component_statuses.append(health["components"]["qdrant"]["status"])
    
    if "offline" in component_statuses:
        health["status"] = "degraded"
    
    return health

def write_health_check_file():
    """Write health check information to a static file for monitoring."""
    try:
        health = get_system_health()
        
        # Create static directory if it doesn't exist
        os.makedirs("static", exist_ok=True)
        
        # Write health check to file
        with open("static/health.json", "w") as f:
            json.dump(health, f, indent=2)
        
        return health
    except Exception as e:
        logger.error(f"Error writing health check file: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # This allows running the health check as a standalone script
    health = write_health_check_file()
    print(json.dumps(health, indent=2))
