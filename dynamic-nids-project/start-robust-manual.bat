@echo off
echo Starting Robust NIDS Backend...
echo.

cd /d "%~dp0"

REM Set warning suppression
set PYTHONWARNINGS=ignore::RuntimeWarning:numpy
set OMP_NUM_THREADS=1

REM Activate environment
call nids_env\Scripts\activate.bat

REM Start robust backend
echo [*] Starting robust backend on http://localhost:8000
echo [*] Press Ctrl+C to stop
echo.

nids_env\Scripts\python.exe backend\main_robust.py

echo.
echo [*] Backend stopped.
pause
