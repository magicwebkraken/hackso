@echo off
echo ========================================
echo Installing Dependencies
echo ========================================
echo.
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   start_web.bat  (to start the web interface)
echo   python app.py  (to start the web interface)
echo.
pause

