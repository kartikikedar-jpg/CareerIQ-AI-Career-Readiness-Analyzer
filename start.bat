
@echo off
title CareerIQ
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)

set "PYTHON=%~dp0.venv\Scripts\python.exe"

"%PYTHON%" -m pip install -r requirements.txt

if errorlevel 1 (
    echo Package installation failed.
    pause
    exit /b
)

cd /d "%~dp0backend"

"%PYTHON%" db.py

start "CareerIQ Server" "%PYTHON%" app.py

timeout /t 5 /nobreak >nul

start "" "http://127.0.0.1:5000/login"

pause
