@echo off
setlocal enabledelayedexpansion

echo HVAC CRM/ERP gRPC Client
echo =======================

:: Set environment variables for gRPC
set GRPC_ENABLED=true
set GRPC_ADDRESS=0.0.0.0
set GRPC_PORT=8080

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

:: Parse command line arguments
set ACTION=status
set CLIENT_ID=test-client
set SUBJECT=Test Email
set TO_EMAIL=test@example.com
set TEXT_CONTENT=This is a test email
set FOLDER=INBOX
set LIMIT=10
set UNREAD_ONLY=true
set SERVICE=grpc

:: Parse arguments
:parse_args
if "%~1"=="" goto :run_client
if /i "%~1"=="--action" (
    set ACTION=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--client-id" (
    set CLIENT_ID=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--subject" (
    set SUBJECT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--to-email" (
    set TO_EMAIL=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--text-content" (
    set TEXT_CONTENT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--folder" (
    set FOLDER=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--limit" (
    set LIMIT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--unread-only" (
    set UNREAD_ONLY=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--service" (
    set SERVICE=%~2
    shift
    shift
    goto :parse_args
)
shift
goto :parse_args

:run_client
:: Run the gRPC client
echo Running gRPC client with action: %ACTION%
python grpc_client.py --action %ACTION% --client-id "%CLIENT_ID%" --subject "%SUBJECT%" --to-email "%TO_EMAIL%" --text-content "%TEXT_CONTENT%" --folder "%FOLDER%" --limit %LIMIT% --unread-only %UNREAD_ONLY% --service "%SERVICE%"
