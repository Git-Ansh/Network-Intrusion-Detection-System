@echo off
echo Installing NIDS Dependencies (Python 3.13 Compatible)...
echo.

REM Activate virtual environment
call nids_env\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing core dependencies first...
pip install wheel setuptools

echo Installing packages individually with pre-compiled binaries...
pip install --only-binary=all numpy==1.26.3
pip install --only-binary=all pandas==2.1.4
pip install --only-binary=all scikit-learn==1.4.0
pip install networkx==3.2.1
pip install joblib==1.3.2
pip install psutil==5.9.6

echo Installing FastAPI and related...
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install python-multipart==0.0.6

echo Installing authentication packages...
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"

echo Installing PyShark...
pip install pyshark==0.6

echo.
echo Dependencies installed successfully!
echo Now you can run: start-backend.bat
pause
