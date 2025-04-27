#!/bin/bash
set -e

# Set default port if not provided
PORT=${PORT:-8501}

# Print environment information for debugging
echo "Starting application with the following configuration:"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Skip database check in production environment
if [ "$SKIP_DB_CHECK" = "true" ]; then
    echo "Skipping database connection check as SKIP_DB_CHECK=true"
else
    # Check if database connection is available (but don't fail if it's not)
    echo "Checking database connection..."
    python -c "
import sys
import time
import os
try:
    import psycopg2
    from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

    print(f'Database config: {DB_HOST}:{DB_PORT}/{DB_NAME}')

    max_retries = 3
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
            break
        except Exception as e:
            retry_count += 1
            print(f'Database connection attempt {retry_count}/{max_retries} failed: {e}')
            if retry_count < max_retries:
                time.sleep(2)

    # Continue even if database connection fails
    if retry_count >= max_retries:
        print('Could not connect to database after multiple attempts')
        print('Continuing anyway to allow application to start...')
except ImportError as e:
    print(f'Import error: {e}')
    print('Continuing without database connection check...')
except Exception as e:
    print(f'Unexpected error during database check: {e}')
    print('Continuing anyway to allow application to start...')
"
fi

# Make sure the port is properly set for Streamlit
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=true

# Start the application
echo "Starting Streamlit application on port $PORT..."
exec streamlit run app.py
