# backend/main_ml_minimal.py

"""
Minimal NIDS backend for Windows
No numpy/sklearn dependencies, pure Python
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import warnings
import os
from typing import Dict, Any

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Import minimal ML services
from ml_services_minimal import get_ml_services, get_model_status

# --- Application Setup ---
app = FastAPI(
    title="Minimal NIDS Backend",
    description="Minimal NIDS backend for Windows compatibility",
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

# Initialize minimal ML services
ml_services = get_ml_services()
print(f"[*] Minimal ML Services initialized")

# --- API Endpoints ---

@app.get("/", summary="API Root")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Minimal NIDS Backend",
        "version": "1.0.0",
        "status": "operational",
        "description": "Windows-compatible NIDS with rule-based detection",
        "endpoints": ["/docs", "/api/health", "/api/ml/status", "/api/ml/test"]
    }

@app.get("/api/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "service_type": "minimal",
        "platform": "windows_compatible"
    }

@app.get("/api/ml/status", summary="ML Services Status")
async def get_ml_status():
    """Get ML services status and capabilities"""
    try:
        model_status = get_model_status()
        model_info = ml_services.get_model_info()
        
        return {
            "ml_available": False,
            "service_type": "minimal_rule_based",
            "models": model_status,
            "model_info": model_info,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "error": str(e),
            "ml_available": False,
            "timestamp": asyncio.get_event_loop().time()
        }

@app.post("/api/ml/predict", summary="Anomaly Prediction")
async def predict_anomaly(feature_data: Dict[str, Any]):
    """Predict anomaly using rule-based detection"""
    try:
        prediction = await ml_services.predict_anomaly(feature_data)
        return {
            "prediction": prediction,
            "input_features": feature_data,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "error": str(e),
            "input_features": feature_data,
            "timestamp": asyncio.get_event_loop().time()
        }

@app.get("/api/ml/test", summary="Test Detection")
async def test_detection():
    """Test anomaly detection with sample data"""
    test_cases = [
        {
            "name": "normal_http",
            "data": {
                'packet_size': 500,
                'protocol': 'TCP',
                'port': 80,
                'time_delta': 0.1
            }
        },
        {
            "name": "large_packet",
            "data": {
                'packet_size': 1500,
                'protocol': 'TCP',
                'port': 443,
                'time_delta': 0.05
            }
        },
        {
            "name": "suspicious_port",
            "data": {
                'packet_size': 200,
                'protocol': 'TCP',
                'port': 1337,
                'time_delta': 0.001
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            prediction = await ml_services.predict_anomaly(test_case["data"])
            results.append({
                "test_case": test_case["name"],
                "input": test_case["data"],
                "prediction": prediction,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "test_case": test_case["name"],
                "input": test_case["data"],
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "test_results": results,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/alerts", summary="Security Alerts")
async def get_alerts():
    """Get simulated security alerts"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "rule_based_detection",
                "severity": "medium",
                "message": "Suspicious traffic pattern detected",
                "timestamp": asyncio.get_event_loop().time()
            }
        ],
        "count": 1,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/stats", summary="System Stats")
async def get_stats():
    """Get system statistics"""
    model_info = ml_services.get_model_info()
    return {
        "system": "minimal_nids",
        "detector_stats": model_info.get("detector_stats", {}),
        "predictions_made": model_info.get("predictions_made", 0),
        "timestamp": asyncio.get_event_loop().time()
    }

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 50)
    print("🚀 Minimal NIDS Backend Starting")
    print("=" * 50)
    print("🔧 Service Type: Rule-based Detection")
    print("🪟 Platform: Windows Compatible")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
