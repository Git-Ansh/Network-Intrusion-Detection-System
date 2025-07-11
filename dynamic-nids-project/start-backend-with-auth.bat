@echo off
echo ========================================
echo Starting NIDS Backend with Authentication
echo ========================================

cd /d "%~dp0"

REM Set environment variables
set PYTHONWARNINGS=ignore
set PYTHONPATH=%cd%\backend

REM Activate virtual environment
echo [*] Activating virtual environment...
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call nids_env\Scripts\activate.bat

REM Start the authenticated backend
echo [*] Starting NIDS backend with authentication...
echo [*] Backend will be available at: http://localhost:8000
echo [*] API Documentation: http://localhost:8000/docs
echo [*] Demo Login: admin / admin123
echo [*] Press Ctrl+C to stop
echo ========================================

cd backend
python main_ml_with_auth.py

pause
