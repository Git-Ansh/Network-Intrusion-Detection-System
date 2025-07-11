@echo off
title NIDS - Service Stopper

echo ================================================================
echo                      NIDS Service Stopper  
echo ================================================================
echo.
echo This will stop all NIDS backend and frontend services.
echo.

REM Stop Python processes (backend)
echo [*] Stopping backend services...
taskkill /f /im python.exe >nul 2>&1
if errorlevel 1 (
    echo [*] No Python processes found
) else (
    echo [✓] Python backend processes stopped
)

REM Stop Node.js processes (frontend)
echo [*] Stopping frontend services...
taskkill /f /im node.exe >nul 2>&1
if errorlevel 1 (
    echo [*] No Node.js processes found
) else (
    echo [✓] Node.js frontend processes stopped
)

REM Stop any remaining uvicorn processes
taskkill /f /im uvicorn.exe >nul 2>&1

echo.
echo [*] Checking for running services on ports...

REM Check if ports are still in use
netstat -an | findstr ":8000 " >nul 2>&1
if errorlevel 1 (
    echo [✓] Port 8000 (backend) is free
) else (
    echo [!] Port 8000 may still be in use
)

netstat -an | findstr ":5173 " >nul 2>&1  
if errorlevel 1 (
    echo [✓] Port 5173 (frontend) is free
) else (
    echo [!] Port 5173 may still be in use
)

echo.
echo ================================================================
echo                     🛑 Services Stopped
echo ================================================================
echo.
echo All NIDS services have been stopped.
echo.
echo To restart the application, run:
echo   🚀 Start NIDS.bat
echo.
echo ================================================================

timeout /t 3 /nobreak >nul
