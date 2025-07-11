@echo off
echo ========================================
echo Testing Enhanced NIDS with ML
echo ========================================

cd /d "%~dp0"

REM Set warning suppression
set PYTHONWARNINGS=ignore::RuntimeWarning:numpy
set OMP_NUM_THREADS=1

REM Activate environment
call nids_env\Scripts\activate.bat

echo [*] Testing enhanced main.py with ML capabilities...
echo [*] Server will start on http://localhost:8000
echo [*] API docs: http://localhost:8000/docs
echo [*] Press Ctrl+C to stop
echo.

nids_env\Scripts\python.exe -W ignore::RuntimeWarning:numpy backend\main.py

echo.
echo [*] Server stopped.
pause
