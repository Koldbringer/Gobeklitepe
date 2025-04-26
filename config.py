import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "hvac_wektory")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "hvac_crm_erp")
DB_USER = os.getenv("DB_USER", "hvac_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = os.getenv("DB_PORT", "5432")

# n8n configuration
N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

# Application settings
APP_NAME = "HVAC CRM/ERP System"
COMPANY_NAME = "HVAC Solutions"
LOGO_PATH = "assets/logo.png"

# Theme configuration
PRIMARY_COLOR = "#1E88E5"
SECONDARY_COLOR = "#FFC107"
BACKGROUND_COLOR = "#F5F5F5"
TEXT_COLOR = "#212121"

# Feature flags
ENABLE_OCR = os.getenv("ENABLE_OCR", "True").lower() == "true"
ENABLE_LLM = os.getenv("ENABLE_LLM", "True").lower() == "true"
ENABLE_QDRANT = os.getenv("ENABLE_QDRANT", "True").lower() == "true"
ENABLE_N8N = os.getenv("ENABLE_N8N", "True").lower() == "true"
