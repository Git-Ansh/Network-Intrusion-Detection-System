# backend/main_ml_simple.py

"""
Simple ML backend without authentication for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import warnings
import os
from typing import Dict, Any

# Suppress warnings at module level
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

# Import ML services without auth
from ml_services import get_ml_services, get_model_status

# --- Application Setup ---
app = FastAPI(
    title="Simple NIDS ML Backend",
    description="Simple ML-enabled NIDS backend for testing",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML services
ml_services = get_ml_services()
print(f"[*] ML Services Available: {ml_services.ml_available}")

# --- API Endpoints ---

@app.get("/", summary="API Root")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Simple ML-Enabled NIDS",
        "version": "1.0.0",
        "status": "operational",
        "ml_enabled": ml_services.ml_available,
        "endpoints": ["/docs", "/api/health", "/api/ml/status", "/api/ml/test"]
    }

@app.get("/api/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "ml_available": ml_services.ml_available
    }

@app.get("/api/ml/status", summary="ML Services Status")
async def get_ml_status():
    """Get ML services status and capabilities"""
    try:
        model_status = get_model_status()
        return {
            "ml_available": ml_services.ml_available,
            "models": model_status,
            "service_type": "advanced" if ml_services.ml_available else "simple",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "error": str(e),
            "ml_available": False,
            "timestamp": asyncio.get_event_loop().time()
        }

@app.post("/api/ml/predict", summary="ML Prediction")
async def predict_anomaly(feature_data: Dict[str, Any]):
    """Predict anomaly using ML models"""
    try:
        prediction = await ml_services.predict_anomaly(feature_data)
        return {
            "prediction": prediction,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "error": str(e),
            "ml_available": ml_services.ml_available,
            "timestamp": asyncio.get_event_loop().time()
        }

@app.get("/api/ml/test", summary="Test ML Functionality")
async def test_ml():
    """Test ML functionality with sample data"""
    try:
        sample_data = {
            'packet_size': 1500,
            'protocol': 'TCP', 
            'port': 80,
            'time_delta': 0.1
        }
        
        prediction = await ml_services.predict_anomaly(sample_data)
        
        return {
            "test": "success",
            "sample_data": sample_data,
            "prediction": prediction,
            "ml_available": ml_services.ml_available,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "test": "failed",
            "error": str(e),
            "ml_available": ml_services.ml_available,
            "timestamp": asyncio.get_event_loop().time()
        }

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 50)
    print("🚀 Simple NIDS ML Backend Starting")
    print("=" * 50)
    print(f"🤖 ML Services: {'Available' if ml_services.ml_available else 'Fallback'}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
