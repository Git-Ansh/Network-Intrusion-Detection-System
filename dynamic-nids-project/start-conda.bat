@echo off
echo Setting up NIDS with Conda (Python 3.13 Compatible)...
echo.

REM Create conda environment
conda create -n nids_conda python=3.11 -y

REM Activate conda environment
call conda activate nids_conda

echo Installing dependencies with conda...
conda install -c conda-forge numpy pandas scikit-learn networkx joblib psutil -y

echo Installing remaining packages with pip...
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install pyshark==0.6
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"
pip install python-multipart==0.0.6

cd backend

echo Training ML models...
python train_models.py

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
