@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP Networking Configuration Utility
echo ============================================

:: Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available in the PATH.
    exit /b 1
)

:: Pass all arguments to the Python script
python update_networking.py %*

:: Print current configuration if no arguments provided
if "%~1"=="" (
    echo.
    echo Current networking configuration:
    python update_networking.py --print
)

echo.
echo To update settings, use parameters like:
echo   update_networking.bat --http-port 8080 --public-domain example.com
echo.
echo For help, use:
echo   update_networking.bat --help
echo.
