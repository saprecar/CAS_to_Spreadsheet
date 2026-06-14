#!/usr/bin/env bash

echo "=========================================="
echo "        CAS Parser Launcher"
echo "=========================================="
echo ""

# Find python executable
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Python is not installed or not added to PATH."
    echo ""
    echo "Download it from: https://www.python.org/downloads/"
    echo ""
    read -p "Press any key to exit..." -n1 -s
    echo ""
    exit 1
fi

# Check requirements
$PYTHON_CMD check_requirements.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Please install requirements first using:"
    echo "  $PYTHON_CMD -m pip install -r requirements.txt"
    echo ""
    read -p "Press any key to exit..." -n1 -s
    echo ""
    exit 1
fi

echo ""
echo "Starting application..."
echo "Open your browser at: http://127.0.0.1:8000"
echo ""

$PYTHON_CMD main.py

echo ""
echo "Application closed."
read -p "Press any key to exit..." -n1 -s
echo ""
