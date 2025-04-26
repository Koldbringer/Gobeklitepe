from supabase import create_client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def is_connected():
    """Check if Supabase client is connected."""
    if not supabase:
        return False
    try:
        # Try a simple query to check connection
        supabase.table('klienci').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return False

# Client-related functions
def get_clients(search=None, limit=100, offset=0):
    """Get clients with optional search filter using Supabase."""
    if not supabase:
        return []
    
    query = supabase.table('klienci').select('*')
    
    if search:
        query = query.or_(f"nazwa.ilike.%{search}%,email.ilike.%{search}%,telefon.ilike.%{search}%")
    
    response = query.order('nazwa').limit(limit).offset(offset).execute()
    return response.data if response else []

def get_client_by_id(client_id):
    """Get a client by ID using Supabase."""
    if not supabase:
        return None
    
    response = supabase.table('klienci').select('*').eq('id', client_id).execute()
    return response.data[0] if response and response.data else None

def create_client(client_data):
    """Create a new client using Supabase."""
    if not supabase:
        return None
    
    response = supabase.table('klienci').insert(client_data).execute()
    return response.data[0]['id'] if response and response.data else None

def update_client(client_id, client_data):
    """Update an existing client using Supabase."""
    if not supabase:
        return False
    
    response = supabase.table('klienci').update(client_data).eq('id', client_id).execute()
    return bool(response and response.data)

# Device-related functions
def get_devices(client_id=None, building_id=None, search=None, limit=100, offset=0):
    """Get devices with optional filters using Supabase."""
    if not supabase:
        return []
    
    # This is a simplified version - in a real app, you'd need to handle the joins properly
    query = supabase.table('urządzenia_hvac').select('*')
    
    if client_id:
        # This assumes you have a view or RPC function that handles the join
        query = query.eq('id_klienta', client_id)
    
    if building_id:
        query = query.eq('id_budynku', building_id)
    
    if search:
        query = query.or_(f"model.ilike.%{search}%,numer_seryjny.ilike.%{search}%")
    
    response = query.order('data_instalacji', desc=True).limit(limit).offset(offset).execute()
    return response.data if response else []

# Service order-related functions
def get_service_orders(status=None, client_id=None, device_id=None, limit=100, offset=0):
    """Get service orders with optional filters using Supabase."""
    if not supabase:
        return []
    
    query = supabase.table('zlecenia_serwisowe').select('*')
    
    if status:
        query = query.eq('status', status)
    
    if client_id:
        query = query.eq('id_klienta', client_id)
    
    if device_id:
        query = query.eq('id_urządzenia', device_id)
    
    response = query.order('data_utworzenia', desc=True).limit(limit).offset(offset).execute()
    return response.data if response else []

# Real-time subscriptions
def subscribe_to_service_orders(callback):
    """Subscribe to changes in service orders."""
    if not supabase:
        return None
    
    return supabase.table('zlecenia_serwisowe').on('*', callback).subscribe()

def subscribe_to_client_updates(client_id, callback):
    """Subscribe to changes for a specific client."""
    if not supabase:
        return None
    
    return supabase.table('klienci').eq('id', client_id).on('*', callback).subscribe()

# Storage functions
def upload_file(bucket, file_path, file_content):
    """Upload a file to Supabase storage."""
    if not supabase:
        return None
    
    response = supabase.storage.from_(bucket).upload(file_path, file_content)
    return response

def get_file_url(bucket, file_path):
    """Get a public URL for a file in Supabase storage."""
    if not supabase:
        return None
    
    return supabase.storage.from_(bucket).get_public_url(file_path)

# Authentication functions (if needed)
def sign_up(email, password):
    """Sign up a new user."""
    if not supabase:
        return None
    
    response = supabase.auth.sign_up({"email": email, "password": password})
    return response

def sign_in(email, password):
    """Sign in an existing user."""
    if not supabase:
        return None
    
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return response

def sign_out():
    """Sign out the current user."""
    if not supabase:
        return None
    
    return supabase.auth.sign_out()
