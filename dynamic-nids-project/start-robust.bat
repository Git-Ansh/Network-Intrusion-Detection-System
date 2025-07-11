@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Robust NIDif "%ML_MODE%"=="robust" (
    echo [*] Starting robust backend with ML services...
    echo [*] Suppressing numpy warnings for Windows compatibility...
    echo [*] Backend will start on http://localhost:8000
    echo [*] Press Ctrl+C to stop the server
    echo.
    nids_env\Scripts\python.exe -W ignore::RuntimeWarning:numpy backend\main_robust.py
) else (
    echo [*] Starting simple backend...
    echo [*] Backend will start on http://localhost:8000
    echo [*] Press Ctrl+C to stop the server
    echo.
    nids_env\Scripts\python.exe backend\main_simple.py
)p (Windows Safe)
echo ========================================

cd /d "%~dp0"

REM Set environment variables to suppress numpy warnings
set PYTHONWARNINGS=ignore::RuntimeWarning:numpy
set OMP_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1

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

REM Install basic requirements
echo [*] Installing basic requirements...
nids_env\Scripts\pip.exe install fastapi uvicorn pyshark networkx python-jose passlib joblib psutil python-multipart

REM Try to install ML dependencies with specific handling for Windows
echo [*] Attempting to install ML dependencies for Windows...

REM First try the latest versions
nids_env\Scripts\pip.exe install --only-binary=all numpy 2>nul
if errorlevel 1 (
    echo [!] Failed to install numpy with binary-only. Trying different approach...
    nids_env\Scripts\pip.exe install numpy==1.24.3 2>nul
)

REM Try pandas
nids_env\Scripts\pip.exe install --only-binary=all pandas 2>nul
if errorlevel 1 (
    echo [!] Failed to install pandas with binary-only. Trying older version...
    nids_env\Scripts\pip.exe install pandas==1.5.3 2>nul
    if errorlevel 1 (
        echo [!] Pandas installation failed completely.
        set PANDAS_AVAILABLE=false
    ) else (
        set PANDAS_AVAILABLE=true
    )
) else (
    set PANDAS_AVAILABLE=true
)

REM Try scikit-learn
if "!PANDAS_AVAILABLE!"=="true" (
    echo [*] Installing scikit-learn...
    nids_env\Scripts\pip.exe install --only-binary=all scikit-learn 2>nul
    if errorlevel 1 (
        echo [!] Failed to install scikit-learn with binary-only. Trying older version...
        nids_env\Scripts\pip.exe install scikit-learn==1.3.0 2>nul
        if errorlevel 1 (
            echo [!] scikit-learn installation failed.
            set SKLEARN_AVAILABLE=false
        ) else (
            set SKLEARN_AVAILABLE=true
        )
    ) else (
        set SKLEARN_AVAILABLE=true
    )
) else (
    set SKLEARN_AVAILABLE=false
)

REM Test ML availability
echo.
echo [*] Testing ML dependencies...
if "!PANDAS_AVAILABLE!"=="true" (
    if "!SKLEARN_AVAILABLE!"=="true" (
        echo [+] Testing pandas and scikit-learn...
        nids_env\Scripts\python.exe -c "import warnings; warnings.filterwarnings('ignore'); import pandas, sklearn; print('[+] Full ML libraries available')" 2>nul
        if errorlevel 1 (
            echo [!] ML libraries test failed. Using simple mode.
            set ML_MODE=simple
        ) else (
            echo [+] ML libraries test passed. Using robust mode.
            set ML_MODE=robust
        )
    ) else (
        echo [!] scikit-learn not available. Using simple mode.
        set ML_MODE=simple
    )
) else (
    echo [!] pandas not available. Using simple mode.
    set ML_MODE=simple
)

REM Start the appropriate backend
echo.
echo ========================================
echo Starting Backend
echo ========================================

if "!ML_MODE!"=="robust" (
    echo [*] Starting robust backend with ML services...
    echo [*] Suppressing numpy warnings for Windows compatibility...
    nids_env\Scripts\python.exe -W ignore::RuntimeWarning:numpy backend\main_robust.py
) else (
    echo [*] Starting simple backend...
    nids_env\Scripts\python.exe backend\main_simple.py
)

echo.
echo [*] Backend stopped.
pause
