@echo off
setlocal enabledelayedexpansion

:: Set default port if not provided
if "%PORT%"=="" set PORT=8080

:: Set public domain if not provided
if "%PUBLIC_DOMAIN%"=="" set PUBLIC_DOMAIN=gobeklitepe-5hzle.kinsta.app

:: Set public port if not provided
if "%PUBLIC_PORT%"=="" set PUBLIC_PORT=443

:: Set public protocol if not provided
if "%PUBLIC_PROTOCOL%"=="" set PUBLIC_PROTOCOL=https

:: Print environment information
echo Starting application with the following configuration:
echo PORT: %PORT%
echo PUBLIC_DOMAIN: %PUBLIC_DOMAIN%
echo PUBLIC_PORT: %PUBLIC_PORT%
echo PUBLIC_PROTOCOL: %PUBLIC_PROTOCOL%
echo Current directory: %CD%

:: Check for any existing WebSocket test lock files and remove them
if exist "websocket_test.lock" (
    echo Removing existing WebSocket test lock file...
    del /f websocket_test.lock
)

:: Set Streamlit environment variables
set STREAMLIT_SERVER_PORT=%PORT%
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_ENABLE_CORS=true
set STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
set STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=false
set STREAMLIT_BROWSER_SERVERADDRESS=%PUBLIC_DOMAIN%
set STREAMLIT_BROWSER_SERVERPORT=%PUBLIC_PORT%

:: Generate networking configuration
echo Generating networking configuration...
python networking_config.py

:: Generate the WebSocket test HTML file
echo Generating WebSocket test file...
python consolidated_websocket_test.py --generate-html --url "%PUBLIC_PROTOCOL%s://%PUBLIC_DOMAIN%/_stcore/stream"

:: Start the application
echo Starting Streamlit application on port %PORT%...
streamlit run app.py
