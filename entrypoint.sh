#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8501}

# Start the application
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
