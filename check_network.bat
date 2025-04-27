@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP Network Health Check
echo ================================

:: Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available in the PATH.
    exit /b 1
)

:: Run the network health check
python network_health_check.py %*

:: Store the exit code
set EXIT_CODE=%ERRORLEVEL%

:: Display additional information based on the result
if %EXIT_CODE% EQU 0 (
    echo.
    echo Network configuration is healthy.
    echo The application should be accessible at:
    python -c "from networking_config import load_config; config = load_config(); print(f'{config.get(\"public_protocol\", \"https\")}://{config.get(\"public_domain\", \"localhost\")}:{config.get(\"public_port\", 443)}')"
) else (
    echo.
    echo Network configuration has issues.
    echo Please check the results above and fix any problems.
    echo You can update the network configuration using:
    echo   update_networking.bat
)

exit /b %EXIT_CODE%
