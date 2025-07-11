@echo off
echo ========================================
echo NIDS ML Services Integration
echo ========================================

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv nids_env
    if errorlevel 1 (
        echo [!] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call nids_env\Scripts\activate.bat

REM Install basic requirements first
echo [*] Installing basic requirements...
nids_env\Scripts\pip.exe install fastapi uvicorn pyshark networkx python-jose passlib joblib psutil python-multipart

REM Try to install ML dependencies
echo [*] Attempting to install ML dependencies...
nids_env\Scripts\pip.exe install pandas==2.1.4 2>nul
if errorlevel 1 (
    echo [!] Failed to install pandas. Trying alternative approaches...
    
    REM Try with older version
    nids_env\Scripts\pip.exe install pandas==1.5.3 2>nul
    if errorlevel 1 (
        echo [!] Pandas installation failed. Using simple mode.
        set ML_MODE=simple
    ) else (
        set ML_MODE=basic
    )
) else (
    set ML_MODE=full
    echo [+] Pandas installed successfully
)

REM Try scikit-learn
if "%ML_MODE%"=="full" (
    echo [*] Installing scikit-learn...
    nids_env\Scripts\pip.exe install scikit-learn==1.4.0 2>nul
    if errorlevel 1 (
        echo [!] scikit-learn installation failed. Trying older version...
        nids_env\Scripts\pip.exe install scikit-learn==1.3.0 2>nul
        if errorlevel 1 (
            echo [!] scikit-learn installation failed. Using basic mode.
            set ML_MODE=basic
        )
    )
)

REM Start appropriate backend based on ML availability
echo.
echo ========================================
echo Starting Backend
echo ========================================

if "%ML_MODE%"=="full" (
    echo [*] Starting with full ML services...
    nids_env\Scripts\python.exe -c "import pandas, sklearn; print('[+] All ML libraries available')"
    if errorlevel 1 (
        echo [!] ML libraries check failed. Falling back to simple mode.
        nids_env\Scripts\python.exe backend\main_simple.py
    ) else (
        nids_env\Scripts\python.exe backend\main_ml.py
    )
) else if "%ML_MODE%"=="basic" (
    echo [*] Starting with basic ML services...
    nids_env\Scripts\python.exe backend\main.py
) else (
    echo [*] Starting in simple mode...
    nids_env\Scripts\python.exe backend\main_simple.py
)

pause
