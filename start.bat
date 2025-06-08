@echo off
cd /d %~dp0

echo === Step 1: Checking Python ===
where python
if errorlevel 1 (
    echo Error: Python not found. Please install Python and add it to PATH
    pause
    exit /b 1
)

echo === Step 2: Setting up environment ===
if exist "venv" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating new virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r h2snotifier/requirements.txt

echo === Step 3: Starting monitor ===
echo Press Ctrl+C to stop the program
cd h2snotifier
python main.py

echo Program stopped
pause
