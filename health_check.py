import os
import sys
import json
from datetime import datetime

def application(environ, start_response):
    """Simple WSGI application for health checks."""
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    # Gather environment information
    env_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "environment": {k: v for k, v in os.environ.items() if k.startswith(('PORT', 'STREAMLIT', 'PYTHON'))},
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir('.')[:10]  # List first 10 files
    }
    
    response_body = json.dumps(env_info, indent=2)
    
    start_response(status, headers)
    return [response_body.encode()]

if __name__ == "__main__":
    # This can be run as a standalone health check server
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('HEALTH_CHECK_PORT', 8000))
    httpd = make_server('', port, application)
    print(f"Serving health check on port {port}...")
    httpd.serve_forever()
