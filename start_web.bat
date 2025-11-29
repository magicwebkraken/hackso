@echo off
cd /d "%~dp0"
echo ========================================
echo  Wallet Scanner - Web Interface
echo ========================================
echo.
echo Checking dependencies...
python -c "import flask, web3, eth_account" 2>nul
if errorlevel 1 (
    echo Dependencies missing! Installing...
    python -m pip install -r requirements.txt --quiet
    echo.
)
echo.
echo Starting Web Interface...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
if errorlevel 1 (
    echo.
    echo ERROR: Could not start the server!
    echo Make sure Python is installed and all dependencies are installed.
    echo Run: install.bat
    pause
)

