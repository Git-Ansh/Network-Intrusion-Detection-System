@echo off
echo Starting NIDS Backend (Simple Version)...
echo.

REM Check if virtual environment exists
if not exist "nids_env" (
    echo Error: Virtual environment not found!
    echo Please run run-local.bat first to set up the environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call nids_env\Scripts\activate.bat

cd backend

echo.
echo Starting backend server (demo mode - no ML dependencies)...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo This version runs with demo data and doesn't require pandas/scikit-learn
echo Press Ctrl+C to stop the server
echo.

uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload
