@echo off
echo Setting up Dynamic Graph-Based NIDS environment...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo Creating Python virtual environment...
python -m venv nids_env

echo Activating virtual environment...
call nids_env\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r backend\requirements.txt

echo Training ML models...
cd backend
python train_models.py
cd ..

echo.
echo Setup complete!
echo.
echo To run the project:
echo 1. Start with Docker: docker-compose up --build
echo 2. Access the dashboard at http://localhost:3000
echo.
echo Default login credentials:
echo Username: testuser
echo Password: testpassword
echo.
pause
