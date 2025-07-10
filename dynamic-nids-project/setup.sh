#!/bin/bash
# setup.sh - Environment setup script for the NIDS project

echo "Setting up Dynamic Graph-Based NIDS environment..."

# Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv nids_env

# Activate virtual environment (Windows)
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source nids_env/Scripts/activate
else
    source nids_env/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Train ML models
echo "Training ML models..."
cd backend
python train_models.py
cd ..

echo "Setup complete!"
echo ""
echo "To run the project:"
echo "1. Start the backend: docker-compose up backend"
echo "2. Start the frontend: docker-compose up frontend"
echo "3. Access the dashboard at http://localhost:3000"
echo ""
echo "Default login credentials:"
echo "Username: testuser"
echo "Password: testpassword"
