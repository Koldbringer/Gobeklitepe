@echo off
echo Stopping any running WebSocket tests...

:: Check for lock file
if exist "websocket_test.lock" (
    echo Found WebSocket test lock file
    
    :: Read PID from lock file
    set /p PID=<websocket_test.lock
    
    :: Try to terminate the process
    echo Attempting to terminate process with PID %PID%
    taskkill /F /PID %PID% 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Successfully terminated process
    ) else (
        echo Process not found or could not be terminated
    )
    
    :: Remove the lock file
    del /f websocket_test.lock
    echo Removed lock file
) else (
    echo No WebSocket test lock file found
)

echo Done
