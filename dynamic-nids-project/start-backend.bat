@echo off
echo Starting NIDS Backend...
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

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing Python dependencies (this may take a few minutes)...
pip install --only-binary=all -r backend\requirements.txt

cd backend

echo Checking for ML models...
if not exist "models" (
    echo Training ML models...
    python train_models.py
) else (
    echo Models found, skipping training...
)

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
