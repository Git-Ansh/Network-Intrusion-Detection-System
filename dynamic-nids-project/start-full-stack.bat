@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo          NIDS - Starting Backend and Frontend
echo ================================================================
echo.

cd /d "%~dp0"

REM Set environment variables for clean operation
set PYTHONWARNINGS=ignore
set PYTHONPATH=%cd%\backend
set OMP_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1

echo [1/5] Checking Python Virtual Environment...
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv nids_env
    if errorlevel 1 (
        echo [!] Failed to create virtual environment
        pause
        exit /b 1
    )
    
    echo [*] Installing Python dependencies...
    nids_env\Scripts\pip.exe install fastapi uvicorn pyshark networkx python-jose passlib joblib psutil python-multipart requests
    if errorlevel 1 (
        echo [!] Failed to install Python dependencies
        pause
        exit /b 1
    )
)

echo [*] Python environment ready
echo.

echo [2/5] Checking Node.js Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo [*] Installing Node.js dependencies...
    npm install
    if errorlevel 1 (
        echo [!] Failed to install frontend dependencies
        pause
        exit /b 1
    )
) else (
    echo [*] Node.js dependencies already installed
)
cd ..
echo.

echo [3/5] Starting Backend Server...
call nids_env\Scripts\activate.bat

REM Start backend in background
start /min cmd /c "cd /d "%cd%\backend" && set PYTHONWARNINGS=ignore && python main_ml_minimal.py"

echo [*] Backend starting on http://localhost:8000
echo [*] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo.

echo [4/5] Starting Frontend Development Server...
cd frontend

REM Start frontend in background  
start /min cmd /c "npm run dev"

echo [*] Frontend starting on http://localhost:5173
echo [*] Waiting for frontend to initialize...
timeout /t 3 /nobreak >nul

cd ..
echo.

echo [5/5] Opening Application in Browser...
timeout /t 2 /nobreak >nul

REM Open both in browser
start http://localhost:5173
start http://localhost:8000/docs

echo.
echo ================================================================
echo                    🚀 NIDS APPLICATION STARTED
echo ================================================================
echo.
echo 🌐 Frontend (React):     http://localhost:5173
echo 🔧 Backend API:          http://localhost:8000  
echo 📚 API Documentation:    http://localhost:8000/docs
echo.
echo ================================================================
echo                        Service Status
echo ================================================================
echo [*] Backend:  Starting (minimal ML backend)
echo [*] Frontend: Starting (React with Vite)
echo [*] Browser:  Opening automatically
echo.
echo ================================================================
echo                      How to Stop Services
echo ================================================================
echo To stop the services:
echo 1. Close this command window to stop monitoring
echo 2. Backend: Ctrl+C in backend terminal or close its window
echo 3. Frontend: Ctrl+C in frontend terminal or close its window
echo.
echo Press any key to open service monitoring dashboard...
pause >nul

echo.
echo ================================================================
echo                    Service Monitoring Dashboard
echo ================================================================
echo.

:monitor_loop
echo [%time%] Checking service status...

REM Check if backend is responding
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo [%time%] ⚠️  Backend not responding on port 8000
) else (
    echo [%time%] ✅ Backend healthy on port 8000
)

REM Check if frontend is responding  
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo [%time%] ⚠️  Frontend not responding on port 5173
) else (
    echo [%time%] ✅ Frontend healthy on port 5173
)

echo.
echo Press 'q' to quit monitoring, 'r' to restart services, or any other key to check again...
choice /c QRC /n /t 10 /d C >nul
if errorlevel 3 goto :monitor_loop
if errorlevel 2 goto :restart_services
if errorlevel 1 goto :end

goto :monitor_loop

:restart_services
echo.
echo [*] Restarting services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [*] Starting backend...
start /min cmd /c "cd /d "%cd%\backend" && set PYTHONWARNINGS=ignore && python main_ml_minimal.py"

echo [*] Starting frontend...
cd frontend
start /min cmd /c "npm run dev"
cd ..

timeout /t 3 /nobreak >nul
goto :monitor_loop

:end
echo.
echo ================================================================
echo                         Shutting Down
echo ================================================================
echo [*] Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo [*] Services stopped
echo.
echo 👋 Thanks for using NIDS! 
echo ================================================================
pause
