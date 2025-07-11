@echo off
title NIDS - Quick Launcher

echo ================================================================
echo                      NIDS Quick Launcher
echo ================================================================
echo.
echo This will start both the backend and frontend servers.
echo.
echo Backend:  http://localhost:8000 (Python/FastAPI)
echo Frontend: http://localhost:5173 (React/Vite)
echo.
echo ================================================================
echo.

cd /d "%~dp0"

REM Quick check for virtual environment
if not exist "nids_env\Scripts\activate.bat" (
    echo [!] Setup required. Running setup first...
    call setup.bat
    if errorlevel 1 (
        echo [!] Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Start the application
echo [*] Starting NIDS Application...
call start-app.bat

REM This window can be closed after the app starts
echo.
echo ================================================================
echo The application should now be starting in separate windows.
echo You can safely close this window.
echo ================================================================
timeout /t 3 /nobreak >nul
