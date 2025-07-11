@echo off
echo ========================================
echo Starting NIDS ML Backend (Clean Mode)
echo ========================================

cd /d "%~dp0"

REM Set environment variables to suppress warnings
set PYTHONWARNINGS=ignore
set PYTHONPATH=%cd%\backend
set OMP_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1

REM Activate virtual environment
echo [*] Activating virtual environment...
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call nids_env\Scripts\activate.bat

REM Start the ML backend
echo [*] Starting ML-enabled NIDS backend...
echo [*] Backend will be available at: http://localhost:8000
echo [*] API Documentation: http://localhost:8000/docs
echo [*] Press Ctrl+C to stop
echo ========================================

cd backend
python -W ignore main_ml.py

pause
