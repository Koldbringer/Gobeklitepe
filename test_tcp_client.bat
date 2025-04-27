@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP TCP Proxy Test Client
echo =================================

:: Set default host and port if not provided
if "%1"=="" (
    set HOST=localhost
) else (
    set HOST=%1
)

if "%2"=="" (
    set PORT=9000
) else (
    set PORT=%2
)

echo Testing TCP connection to %HOST%:%PORT%...
python test_tcp_proxy.py --mode client --host %HOST% --port %PORT%

if %ERRORLEVEL% EQU 0 (
    echo TCP connection test successful!
) else (
    echo TCP connection test failed!
)
