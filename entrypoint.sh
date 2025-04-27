#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8501}

# Check if database connection is available
echo "Checking database connection..."
python -c "
import sys
import time
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.close()
        print('Database connection successful!')
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f'Database connection attempt {retry_count}/{max_retries} failed: {e}')
        if retry_count < max_retries:
            time.sleep(5)
        else:
            print('Could not connect to database after multiple attempts')
            sys.exit(1)
"

# Start the application
echo "Starting Streamlit application..."
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
