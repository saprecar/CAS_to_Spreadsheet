@echo off
title CAS Parser Launcher

echo ==========================================
echo         CAS Parser Launcher
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not added to PATH.
    echo.
    echo Download it from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: Check requirements
python check_requirements.py

if errorlevel 1 (
    echo.
    echo.
    echo Please run install_requirements.bat
    echo.
    pause
    exit /b
)

echo.
echo Starting application...
echo.

python main.py

echo.
echo Application closed.
pause