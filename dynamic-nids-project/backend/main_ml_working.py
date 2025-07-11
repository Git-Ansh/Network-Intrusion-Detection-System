# backend/main_ml_working.py

"""
Working FastAPI backend with ML services
Simple, functional version that starts reliably
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import warnings
import os
from typing import Dict, Any

# Suppress warnings at module level
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from auth import router as auth_router, get_current_user
from ml_services import get_ml_services, get_model_status

# --- Application Setup ---
app = FastAPI(
    title="NIDS ML Backend (Working)",
    description="Working ML-enabled NIDS backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001", 
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML services
ml_services = get_ml_services()
print(f"[*] ML Services Available: {ml_services.ml_available}")

# Include authentication routes
app.include_router(auth_router, tags=["Authentication"])

# --- API Endpoints ---

@app.get("/", summary="API Root")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "ML-Enabled Network Intrusion Detection System",
        "version": "1.0.0",
        "status": "operational",
        "ml_enabled": ml_services.ml_available,
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "ml_status": "/api/ml/status",
            "ml_predict": "/api/ml/predict"
        }
    }

@app.get("/api/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "ml_services": "running" if ml_services.ml_available else "fallback",
            "authentication": "running"
        }
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
        raise HTTPException(status_code=500, detail=f"Failed to get ML status: {str(e)}")

@app.post("/api/ml/predict", dependencies=[Depends(get_current_user)], summary="ML Prediction")
async def predict_anomaly(feature_data: Dict[str, Any]):
    """Predict anomaly using ML models"""
    try:
        prediction = await ml_services.predict_anomaly(feature_data)
        return {
            "prediction": prediction,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/test/ml", summary="Test ML Functionality")
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

@app.get("/api/alerts", dependencies=[Depends(get_current_user)], summary="Get Security Alerts")
async def get_alerts():
    """Get mock security alerts for testing"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "anomaly_detected",
                "severity": "medium",
                "message": "Unusual traffic pattern detected",
                "timestamp": asyncio.get_event_loop().time()
            }
        ],
        "count": 1,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/graph/data", dependencies=[Depends(get_current_user)], summary="Get Graph Data")
async def get_graph_data():
    """Get mock graph data for testing"""
    return {
        "nodes": [
            {"id": "192.168.1.1", "type": "host", "connections": 5},
            {"id": "192.168.1.2", "type": "host", "connections": 3}
        ],
        "edges": [
            {"source": "192.168.1.1", "target": "192.168.1.2", "weight": 10}
        ],
        "stats": {"total_nodes": 2, "total_edges": 1},
        "timestamp": asyncio.get_event_loop().time()
    }

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("🚀 NIDS ML Backend Starting Up")
    print("=" * 60)
    print(f"🤖 ML Services: {'Advanced' if ml_services.ml_available else 'Simple'}")
    print(f"🔐 Authentication: Enabled")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🛑 NIDS ML Backend Shutting Down...")
    print("👋 Goodbye!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
