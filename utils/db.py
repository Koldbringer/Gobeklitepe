import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

def get_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """Execute a query and return the results."""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return True
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

def query_to_dataframe(query, params=None):
    """Execute a query and return the results as a pandas DataFrame."""
    result = execute_query(query, params)
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()

# Client-related queries
def get_clients(search=None, limit=100, offset=0):
    """Get clients with optional search filter."""
    query = """
    SELECT * FROM klienci
    WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND (nazwa ILIKE %s OR email ILIKE %s OR telefon ILIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    query += " ORDER BY nazwa LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return execute_query(query, params)

def get_client_by_id(client_id):
    """Get a client by ID."""
    query = "SELECT * FROM klienci WHERE id = %s"
    result = execute_query(query, (client_id,))
    return result[0] if result else None

def create_client(client_data):
    """Create a new client."""
    query = """
    INSERT INTO klienci (
        nazwa, email, telefon, adres, typ_klienta, 
        ocena_zamożności, notatki
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id
    """
    params = (
        client_data.get('nazwa'),
        client_data.get('email'),
        client_data.get('telefon'),
        client_data.get('adres'),
        client_data.get('typ_klienta'),
        client_data.get('ocena_zamożności'),
        client_data.get('notatki')
    )
    result = execute_query(query, params)
    return result[0]['id'] if result else None

def update_client(client_id, client_data):
    """Update an existing client."""
    query = """
    UPDATE klienci SET
        nazwa = %s,
        email = %s,
        telefon = %s,
        adres = %s,
        typ_klienta = %s,
        ocena_zamożności = %s,
        notatki = %s
    WHERE id = %s
    """
    params = (
        client_data.get('nazwa'),
        client_data.get('email'),
        client_data.get('telefon'),
        client_data.get('adres'),
        client_data.get('typ_klienta'),
        client_data.get('ocena_zamożności'),
        client_data.get('notatki'),
        client_id
    )
    return execute_query(query, params, fetch=False)

# Device-related queries
def get_devices(client_id=None, building_id=None, search=None, limit=100, offset=0):
    """Get devices with optional filters."""
    query = """
    SELECT u.*, b.nazwa as nazwa_budynku, k.nazwa as nazwa_klienta
    FROM urządzenia_hvac u
    LEFT JOIN budynki b ON u.id_budynku = b.id
    LEFT JOIN klienci k ON b.id_klienta = k.id
    WHERE 1=1
    """
    params = []
    
    if client_id:
        query += " AND b.id_klienta = %s"
        params.append(client_id)
    
    if building_id:
        query += " AND u.id_budynku = %s"
        params.append(building_id)
    
    if search:
        query += " AND (u.model ILIKE %s OR u.numer_seryjny ILIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    query += " ORDER BY u.data_instalacji DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return execute_query(query, params)

def get_device_by_id(device_id):
    """Get a device by ID."""
    query = """
    SELECT u.*, b.nazwa as nazwa_budynku, k.nazwa as nazwa_klienta
    FROM urządzenia_hvac u
    LEFT JOIN budynki b ON u.id_budynku = b.id
    LEFT JOIN klienci k ON b.id_klienta = k.id
    WHERE u.id = %s
    """
    result = execute_query(query, (device_id,))
    return result[0] if result else None

# Building-related queries
def get_buildings(client_id=None, search=None, limit=100, offset=0):
    """Get buildings with optional filters."""
    query = """
    SELECT b.*, k.nazwa as nazwa_klienta
    FROM budynki b
    LEFT JOIN klienci k ON b.id_klienta = k.id
    WHERE 1=1
    """
    params = []
    
    if client_id:
        query += " AND b.id_klienta = %s"
        params.append(client_id)
    
    if search:
        query += " AND (b.nazwa ILIKE %s OR b.adres ILIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    query += " ORDER BY b.nazwa LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return execute_query(query, params)

# Service order-related queries
def get_service_orders(status=None, client_id=None, device_id=None, limit=100, offset=0):
    """Get service orders with optional filters."""
    query = """
    SELECT z.*, k.nazwa as nazwa_klienta, u.model as model_urządzenia
    FROM zlecenia_serwisowe z
    LEFT JOIN klienci k ON z.id_klienta = k.id
    LEFT JOIN urządzenia_hvac u ON z.id_urządzenia = u.id
    WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND z.status = %s"
        params.append(status)
    
    if client_id:
        query += " AND z.id_klienta = %s"
        params.append(client_id)
    
    if device_id:
        query += " AND z.id_urządzenia = %s"
        params.append(device_id)
    
    query += " ORDER BY z.data_utworzenia DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return execute_query(query, params)

# Dashboard queries
def get_dashboard_metrics():
    """Get metrics for the dashboard."""
    metrics = {}
    
    # Total clients
    query = "SELECT COUNT(*) as count FROM klienci"
    result = execute_query(query)
    metrics['total_clients'] = result[0]['count'] if result else 0
    
    # Total devices
    query = "SELECT COUNT(*) as count FROM urządzenia_hvac"
    result = execute_query(query)
    metrics['total_devices'] = result[0]['count'] if result else 0
    
    # Active service orders
    query = "SELECT COUNT(*) as count FROM zlecenia_serwisowe WHERE status != 'zakończone'"
    result = execute_query(query)
    metrics['active_orders'] = result[0]['count'] if result else 0
    
    # Orders by status
    query = """
    SELECT status, COUNT(*) as count 
    FROM zlecenia_serwisowe 
    GROUP BY status
    """
    result = execute_query(query)
    metrics['orders_by_status'] = result if result else []
    
    # Recent clients
    query = """
    SELECT * FROM klienci 
    ORDER BY data_rejestracji DESC 
    LIMIT 5
    """
    result = execute_query(query)
    metrics['recent_clients'] = result if result else []
    
    # Upcoming service orders
    query = """
    SELECT z.*, k.nazwa as nazwa_klienta 
    FROM zlecenia_serwisowe z
    LEFT JOIN klienci k ON z.id_klienta = k.id
    WHERE z.status = 'przypisane' AND z.data_planowana >= CURRENT_DATE
    ORDER BY z.data_planowana
    LIMIT 5
    """
    result = execute_query(query)
    metrics['upcoming_orders'] = result if result else []
    
    return metrics
