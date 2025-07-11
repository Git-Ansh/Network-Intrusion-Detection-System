# backend/main_ml_safe.py

"""
Enhanced FastAPI backend with integrated ML services (Safe Version)
Provides adaptive ML functionality with fallbacks
Safe initialization that doesn't block on network interface detection
"""

from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
import warnings
import os
from typing import List

# Suppress warnings at module level
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from processor import PacketProcessor
from graph_manager import GraphManager
from graph_analyzer import GraphAnalyzer
from auth import router as auth_router, get_current_user
from ml_services import get_ml_services, get_model_status

# --- Application Setup ---
app = FastAPI(
    title="Dynamic Graph-Based NIDS API with ML Services (Safe)",
    description="Provides real-time network graph data, security alerts, and ML-powered anomaly detection.",
    version="2.0.0"
)

# Enhanced CORS configuration for multiple frontend ports
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

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_messages_sent': 0
        }
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.stats['total_connections'] += 1
        self.stats['active_connections'] = len(self.active_connections)
        print(f"[WebSocket] Client connected. Active connections: {self.stats['active_connections']}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.stats['active_connections'] = len(self.active_connections)
        print(f"[WebSocket] Client disconnected. Active connections: {self.stats['active_connections']}")
    
    async def broadcast(self, message: str):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                    self.stats['total_messages_sent'] += 1
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

# --- Global Services ---
# Initialize core services
packet_procsr = PacketProcessor()
graph_mgr = GraphManager()
graph_anlzr = GraphAnalyzer()
connection_manager = ConnectionManager()
ml_services = get_ml_services()

# Traffic sniffer will be initialized on demand
traffic_snffr = None

print("[*] Core services initialized")
print(f"[*] ML Services Available: {ml_services.ml_available}")

# Include authentication routes
app.include_router(auth_router, tags=["Authentication"])

# --- Startup Functions ---
def get_default_interface():
    """Get default network interface safely"""
    try:
        import psutil
        interfaces = psutil.net_if_addrs()
        for interface_name, addresses in interfaces.items():
            if interface_name != 'lo' and any(addr.family == 2 for addr in addresses):  # IPv4
                return interface_name
        return 'eth0'  # fallback
    except:
        return 'eth0'  # fallback

def init_traffic_sniffer():
    """Initialize traffic sniffer on demand"""
    global traffic_snffr
    if traffic_snffr is None:
        try:
            from sniffer import TrafficSniffer
            default_interface = get_default_interface()
            print(f"[*] Using network interface: {default_interface}")
            traffic_snffr = TrafficSniffer(
                interface=default_interface, 
                packet_callback=packet_procsr.process_packet
            )
            print("[*] Traffic sniffer initialized")
        except Exception as e:
            print(f"[!] Failed to initialize traffic sniffer: {e}")
    return traffic_snffr

# --- API Endpoints ---

@app.get("/", summary="API Root")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Dynamic Graph-Based Network Intrusion Detection System with ML Services",
        "version": "2.0.0",
        "status": "operational",
        "ml_enabled": ml_services.ml_available,
        "endpoints": {
            "docs": "/docs",
            "graph_data": "/api/graph/data",
            "alerts": "/api/alerts",
            "ml_status": "/api/ml/status",
            "start_capture": "/api/traffic/start",
            "stop_capture": "/api/traffic/stop"
        }
    }

@app.get("/api/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": json.loads(json.dumps(asyncio.get_event_loop().time())),
        "services": {
            "packet_processor": "running",
            "graph_manager": "running", 
            "graph_analyzer": "running",
            "ml_services": "running" if ml_services.ml_available else "fallback",
            "traffic_sniffer": "initialized" if traffic_snffr else "not_initialized"
        }
    }

@app.get("/api/graph/data", dependencies=[Depends(get_current_user)], summary="Get Graph Data")
async def get_graph_data():
    """Get current network graph data"""
    try:
        graph_data = graph_mgr.get_graph_data()
        return {
            "nodes": graph_data.get("nodes", []),
            "edges": graph_data.get("edges", []),
            "stats": graph_data.get("stats", {}),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")

@app.get("/api/alerts", dependencies=[Depends(get_current_user)], summary="Get Security Alerts")
async def get_alerts():
    """Get current security alerts"""
    try:
        alerts = graph_anlzr.get_alerts()
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

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
async def predict_anomaly(feature_data: dict):
    """Predict anomaly using ML models"""
    try:
        prediction = await ml_services.predict_anomaly(feature_data)
        return {
            "prediction": prediction,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/traffic/start", dependencies=[Depends(get_current_user)], summary="Start Traffic Capture")
async def start_capture():
    """Start network traffic capture"""
    try:
        sniffer = init_traffic_sniffer()
        if sniffer and not getattr(sniffer, 'is_running', False):
            asyncio.create_task(sniffer.start_capture())
            return {"message": "Traffic capture started", "status": "success"}
        else:
            return {"message": "Traffic capture already running", "status": "info"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start capture: {str(e)}")

@app.post("/api/traffic/stop", dependencies=[Depends(get_current_user)], summary="Stop Traffic Capture")  
async def stop_capture():
    """Stop network traffic capture"""
    try:
        if traffic_snffr:
            await traffic_snffr.stop_capture()
            return {"message": "Traffic capture stopped", "status": "success"}
        else:
            return {"message": "Traffic capture not running", "status": "info"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop capture: {str(e)}")

@app.get("/api/stats", summary="System Statistics")
async def get_stats():
    """Get system statistics"""
    return {
        "websocket_stats": connection_manager.stats,
        "graph_stats": graph_mgr.get_stats(),
        "ml_stats": ml_services.get_model_info() if hasattr(ml_services, 'get_model_info') else {},
        "timestamp": asyncio.get_event_loop().time()
    }

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await connection_manager.connect(websocket)
    
    try:
        while True:
            # Send periodic updates
            data = {
                "type": "update",
                "graph": graph_mgr.get_graph_data(),
                "alerts": graph_anlzr.get_alerts(),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await websocket.send_text(json.dumps(data))
            
            try:
                # Wait for client messages (optional)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                # Handle client messages if needed
                client_message = json.loads(data)
                if client_message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_text(json.dumps({"type": "keepalive"}))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("🚀 NIDS with ML Services Starting Up (Safe Mode)")
    print("=" * 60)
    print(f"🤖 ML Services: {'Advanced' if ml_services.ml_available else 'Simple'}")
    print(f"📊 Graph Analysis: Enabled")
    print(f"🔐 Authentication: Enabled")
    print(f"🌐 Traffic Sniffer: On-demand initialization")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🛑 NIDS Shutting Down...")
    try:
        if traffic_snffr:
            await traffic_snffr.stop_capture()
            print("✅ Traffic capture stopped")
    except:
        pass
    print("👋 Goodbye!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
