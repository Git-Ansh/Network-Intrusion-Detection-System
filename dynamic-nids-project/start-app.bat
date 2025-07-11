@echo off
echo ================================================================
echo          NIDS - Quick Start (Backend + Frontend)
echo ================================================================

cd /d "%~dp0"

REM Set environment variables
set PYTHONWARNINGS=ignore
set PYTHONPATH=%cd%\backend

echo [*] Starting NIDS Application...
echo.

REM Check prerequisites
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Python virtual environment not found. 
    echo [*] Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [!] Frontend dependencies not found.
    echo [*] Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo [!] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
)

echo [1/3] Starting Backend Server...
call nids_env\Scripts\activate.bat
start "NIDS Backend" cmd /k "cd /d "%cd%\backend" && set PYTHONWARNINGS=ignore && echo Starting backend server... && python main_ml_minimal.py"

echo [*] Backend starting on http://localhost:8000
echo [*] Waiting for backend to start...
timeout /t 4 /nobreak >nul

echo.
echo [2/3] Starting Frontend Server...
cd frontend
start "NIDS Frontend" cmd /k "echo Starting frontend server... && npm run dev"
cd ..

echo [*] Frontend starting on http://localhost:5173
echo [*] Waiting for frontend to start...
timeout /t 4 /nobreak >nul

echo.
echo [3/3] Opening in Browser...
timeout /t 2 /nobreak >nul

start http://localhost:5173
start http://localhost:8000/docs

echo.
echo ================================================================
echo                    🚀 NIDS APPLICATION READY
echo ================================================================
echo.
echo 🌐 Frontend:         http://localhost:5173
echo 🔧 Backend API:      http://localhost:8000
echo 📚 API Docs:         http://localhost:8000/docs
echo.
echo Two new command windows have opened:
echo   - "NIDS Backend" (Python FastAPI server)  
echo   - "NIDS Frontend" (React development server)
echo.
echo To stop the application:
echo   Close both command windows or press Ctrl+C in each
echo.
echo ================================================================

echo Press any key to test the API connection...
pause >nul

echo.
echo Testing API connection...
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend not responding yet. Please wait a moment and try again.
) else (
    echo ✅ Backend is healthy and responding!
)

echo.
echo 🎉 Setup complete! You can now close this window.
echo    The backend and frontend will continue running.
pause
