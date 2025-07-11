# backend/main_ml_with_auth.py

"""
Minimal NIDS backend with authentication for frontend compatibility
Windows-compatible with simple auth implementation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import asyncio
import warnings
import os
from typing import Dict, Any

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Import minimal ML services
from ml_services_minimal import get_ml_services, get_model_status

# --- Simple Authentication Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simple in-memory user for demo
DEMO_USER = {
    "username": "admin",
    "password": "admin123",
    "full_name": "NIDS Administrator"
}

def authenticate_user(username: str, password: str):
    """Simple authentication check"""
    if username == DEMO_USER["username"] and password == DEMO_USER["password"]:
        return DEMO_USER
    return None

def create_access_token(username: str):
    """Create a simple token (not JWT for simplicity)"""
    return f"token_{username}_{hash(username + 'secret')}"

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    if token.startswith("token_admin_"):
        return DEMO_USER
    raise HTTPException(status_code=401, detail="Invalid authentication")

# --- Application Setup ---
app = FastAPI(
    title="NIDS Backend with Auth",
    description="NIDS backend with authentication for frontend compatibility",
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
print(f"[*] ML Services initialized with authentication")

# --- Authentication Endpoints ---

@app.post("/token", summary="User Login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user["username"])
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", summary="Get Current User")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "full_name": current_user["full_name"]
    }

# --- API Endpoints ---

@app.get("/", summary="API Root")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "NIDS Backend with Authentication",
        "version": "1.0.0",
        "status": "operational",
        "description": "Windows-compatible NIDS with authentication and rule-based detection",
        "auth_info": {
            "demo_username": "admin",
            "demo_password": "admin123"
        },
        "endpoints": ["/docs", "/api/health", "/api/ml/status", "/api/ml/test", "/token"]
    }

@app.get("/api/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "service_type": "minimal_with_auth",
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

@app.post("/api/ml/predict", dependencies=[Depends(get_current_user)], summary="Anomaly Prediction")
async def predict_anomaly(feature_data: Dict[str, Any]):
    """Predict anomaly using rule-based detection (requires auth)"""
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
    """Test anomaly detection with sample data (no auth required)"""
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

@app.get("/api/alerts", dependencies=[Depends(get_current_user)], summary="Security Alerts")
async def get_alerts():
    """Get simulated security alerts (requires auth)"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "rule_based_detection",
                "severity": "medium",
                "message": "Suspicious traffic pattern detected",
                "timestamp": asyncio.get_event_loop().time()
            },
            {
                "id": 2,
                "type": "port_scan",
                "severity": "high",
                "message": "Potential port scan detected from suspicious IP",
                "timestamp": asyncio.get_event_loop().time() - 300
            }
        ],
        "count": 2,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/graph/data", dependencies=[Depends(get_current_user)], summary="Graph Data")
async def get_graph_data():
    """Get mock network graph data (requires auth)"""
    return {
        "nodes": [
            {"id": "192.168.1.1", "type": "host", "connections": 5, "label": "Gateway"},
            {"id": "192.168.1.2", "type": "host", "connections": 3, "label": "Workstation"},
            {"id": "192.168.1.100", "type": "host", "connections": 1, "label": "Server"},
            {"id": "10.0.0.1", "type": "external", "connections": 2, "label": "External"}
        ],
        "edges": [
            {"source": "192.168.1.1", "target": "192.168.1.2", "weight": 10, "type": "normal"},
            {"source": "192.168.1.1", "target": "192.168.1.100", "weight": 5, "type": "normal"},
            {"source": "192.168.1.2", "target": "10.0.0.1", "weight": 3, "type": "suspicious"}
        ],
        "stats": {
            "total_nodes": 4,
            "total_edges": 3,
            "suspicious_connections": 1
        },
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/api/stats", summary="System Stats")
async def get_stats():
    """Get system statistics"""
    model_info = ml_services.get_model_info()
    return {
        "system": "nids_with_auth",
        "detector_stats": model_info.get("detector_stats", {}),
        "predictions_made": model_info.get("predictions_made", 0),
        "auth_info": "Simple token-based authentication",
        "timestamp": asyncio.get_event_loop().time()
    }

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 50)
    print("🚀 NIDS Backend with Auth Starting")
    print("=" * 50)
    print("🔧 Service Type: Rule-based Detection")
    print("🔐 Authentication: Enabled (demo credentials)")
    print("👤 Demo Login: admin / admin123")
    print("🪟 Platform: Windows Compatible")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
