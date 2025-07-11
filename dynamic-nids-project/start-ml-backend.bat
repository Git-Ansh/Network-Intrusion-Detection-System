@echo off
echo ========================================
echo Starting NIDS with ML Services
echo ========================================

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call nids_env\Scripts\activate.bat

REM Check if ML dependencies are installed
echo [*] Checking ML dependencies...
nids_env\Scripts\python.exe -c "import pandas, sklearn; print('[+] ML libraries available')" 2>nul
if errorlevel 1 (
    echo [!] ML libraries not available. Installing...
    nids_env\Scripts\pip.exe install pandas==2.1.4 scikit-learn==1.4.0
    if errorlevel 1 (
        echo [!] Failed to install ML dependencies. Starting in simple mode...
        echo [*] Starting backend with simple ML...
        nids_env\Scripts\python.exe backend\main_simple.py
        goto :end
    )
)

REM Try to start with full ML backend
echo [*] Starting backend with ML services...
nids_env\Scripts\python.exe backend\main_ml.py

:end
pause
