@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP TCP Proxy Test Server
echo =================================

:: Set default port if not provided
if "%1"=="" (
    set PORT=9000
) else (
    set PORT=%1
)

echo Starting TCP server on port %PORT%...
python test_tcp_proxy.py --mode server --port %PORT%
