@echo off
REM Production startup script for Windows
REM Uses Gunicorn for production deployment

cd /d "%~dp0"

echo ========================================
echo Wallet Scanner - Production Mode
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import gunicorn" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

REM Load environment variables from .env if it exists
if exist ".env" (
    echo Loading environment from .env...
    for /f "tokens=*" %%a in (.env) do (
        set "%%a"
    )
)

REM Start with Gunicorn
echo Starting Gunicorn server...
echo.
gunicorn --config gunicorn_config.py app:app

pause

