@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP gRPC Server
echo =======================

:: Set environment variables for gRPC
set GRPC_ENABLED=true
set GRPC_ADDRESS=0.0.0.0
set GRPC_PORT=8080
set GRPC_MAX_WORKERS=10
set GRPC_REFLECTION_ENABLED=true

:: Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available in the PATH.
    exit /b 1
)

:: Check if generated code exists
if not exist "generated\service_pb2.py" (
    echo Generating gRPC code...
    python generate_grpc.py
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to generate gRPC code.
        exit /b 1
    )
)

:: Start the gRPC server
echo Starting gRPC server on %GRPC_ADDRESS%:%GRPC_PORT%...
python grpc_server.py
