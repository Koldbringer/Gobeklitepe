@echo off
echo ========================================
echo  HVAC CRM/ERP Windows Deployment Script
echo ========================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Please install Python first.
    exit /b 1
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Please update the .env file with your actual configuration values.
    ) else (
        echo .env.example file not found. Please create a .env file manually.
        exit /b 1
    )
)

REM Create necessary directories
echo Creating necessary directories...
mkdir assets 2>nul
mkdir nginx\ssl 2>nul
mkdir nginx\logs 2>nul

REM Start the application
echo Starting the application...
echo The application will be available at http://localhost:8501
start "" http://localhost:8501
streamlit run app.py

echo ========================================
echo  Deployment Complete
echo ========================================
