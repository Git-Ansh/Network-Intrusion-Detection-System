@echo off
echo Installing minimal FastAPI dependencies...
echo.

call nids_env\Scripts\activate.bat

echo Installing only essential packages...
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install python-multipart==0.0.6

echo.
echo Dependencies installed! Starting backend...
echo.

cd backend
uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload
