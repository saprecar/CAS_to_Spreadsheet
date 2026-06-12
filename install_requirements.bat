@echo off
title Install Python Requirements

echo Checking Python...
python --version
if errorlevel 1 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
python -m pip install -r requirements.txt

echo.
echo ==========================================
echo All dependencies installed successfully.
echo ==========================================
pause