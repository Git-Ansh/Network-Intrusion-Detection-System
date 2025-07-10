@echo off
echo Starting NIDS System Locally...
echo.

REM Check if Python virtual environment exists
if not exist "nids_env" (
    echo Creating Python virtual environment...
    python -m venv nids_env
)

echo Activating virtual environment...
call nids_env\Scripts\activate.bat

echo Installing/updating Python dependencies...
pip install -r backend\requirements.txt

echo Training ML models (if needed)...
cd backend
if not exist "models" (
    echo Models directory not found, training models...
    python train_models.py
) else (
    echo Models already exist, skipping training...
)

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
start /B uvicorn main:app --host 0.0.0.0 --port 8000 --reload

cd ..\frontend

echo.
echo Installing frontend dependencies...
call npm install

echo.
echo Starting frontend development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Login credentials:
echo Username: testuser
echo Password: testpassword
echo.

npm run dev
