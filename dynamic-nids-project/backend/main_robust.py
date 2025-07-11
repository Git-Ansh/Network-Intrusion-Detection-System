# backend/main_robust.py

"""
Robust FastAPI backend that handles Windows numpy/pandas issues
Uses robust ML services with comprehensive fallbacks
"""

from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from typing import List
import warnings

# Suppress numpy warnings early
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')
warnings.filterwarnings('ignore', message='.*MINGW-W64.*')

from sniffer import TrafficSniffer
from processor import PacketProcessor
from graph_manager import GraphManager
from graph_analyzer import GraphAnalyzer
from auth import router as auth_router, get_current_user

# Import robust ML services
try:
    from ml_services_robust import get_robust_ml_services
    ROBUST_ML_AVAILABLE = True
    print("[*] Robust ML services loaded")
except ImportError as e:
    print(f"[!] Robust ML services not available: {e}")
    ROBUST_ML_AVAILABLE = False
    
    # Fallback to simple detector
    try:
        from simple_detector import SimpleAnomalyDetector
        SIMPLE_DETECTOR_AVAILABLE = True
    except ImportError:
        SIMPLE_DETECTOR_AVAILABLE = False

# --- Application Setup ---
app = FastAPI(
    title="Robust Dynamic Graph-Based NIDS API",
    description="Windows-compatible real-time network intrusion detection with robust ML services.",
    version="2.1.0"
)

# Enhanced CORS configuration
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

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'errors': 0
        }

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.stats['total_connections'] += 1
            self.stats['active_connections'] = len(self.active_connections)
            print(f"[*] WebSocket connected. Active: {len(self.active_connections)}")
        except Exception as e:
            print(f"[!] WebSocket connection error: {e}")
            self.stats['errors'] += 1

    def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            self.stats['active_connections'] = len(self.active_connections)
            print(f"[*] WebSocket disconnected. Active: {len(self.active_connections)}")
        except Exception as e:
            print(f"[!] WebSocket disconnect error: {e}")

    async def broadcast(self, message: str):
        if not self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                self.stats['messages_sent'] += 1
            except Exception as e:
                print(f"[!] Broadcast error: {e}")
                disconnected.append(connection)
                self.stats['errors'] += 1
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

# --- Core Components ---
connection_manager = ConnectionManager()
graph_mgr = GraphManager(ttl=300)
graph_anlyzr = GraphAnalyzer(graph_mgr)

# Initialize ML services based on availability
if ROBUST_ML_AVAILABLE:
    ml_services = get_robust_ml_services()
    ML_MODE = "robust"
    print("[*] Using robust ML services")
elif SIMPLE_DETECTOR_AVAILABLE:
    ml_services = SimpleAnomalyDetector()
    ML_MODE = "simple"
    print("[*] Using simple detector")
else:
    ml_services = None
    ML_MODE = "none"
    print("[*] No ML services available")

# Enhanced analysis pipeline
async def robust_analysis_pipeline(feature_vector):
    """
    Robust analysis pipeline with comprehensive error handling
    """
    try:
        # ML-based anomaly detection
        ml_results = None
        if ml_services:
            try:
                if hasattr(ml_services, 'predict_anomaly'):
                    ml_results = await ml_services.predict_anomaly(feature_vector)
                elif hasattr(ml_services, 'predict'):
                    ml_results = await ml_services.predict(feature_vector)
            except Exception as e:
                print(f"[!] ML prediction error: {e}")
                ml_results = {
                    'is_anomaly': False,
                    'confidence': 0.0,
                    'error': str(e),
                    'model_type': 'error_fallback'
                }
        
        # Update graph with ML results
        try:
            await graph_mgr.update_graph(feature_vector, ml_results)
        except Exception as e:
            print(f"[!] Graph update error: {e}")
        
        # Send alerts for anomalies
        if ml_results and ml_results.get('is_anomaly'):
            try:
                severity = "HIGH" if ml_results.get('confidence', 0) > 0.8 else "MEDIUM"
                alert = {
                    "type": "ML_Anomaly",
                    "timestamp": feature_vector.get('timestamp', 'unknown'),
                    "severity": severity,
                    "message": f"Anomaly detected: {feature_vector.get('src_addr', 'unknown')} → {feature_vector.get('dst_addr', 'unknown')}",
                    "details": {
                        "packet_info": {
                            "src_addr": feature_vector.get('src_addr'),
                            "dst_addr": feature_vector.get('dst_addr'),
                            "src_port": feature_vector.get('src_port'),
                            "dst_port": feature_vector.get('dst_port'),
                            "protocol": feature_vector.get('protocol'),
                            "packet_length": feature_vector.get('packet_length')
                        },
                        "ml_prediction": ml_results
                    }
                }
                await connection_manager.broadcast(json.dumps(alert))
            except Exception as e:
                print(f"[!] Alert broadcast error: {e}")
                
    except Exception as e:
        print(f"[!] Analysis pipeline error: {e}")
        logging.error(f"Analysis pipeline error: {e}")

# Alert handler for graph analyzer
async def alert_handler(alert):
    try:
        await connection_manager.broadcast(json.dumps(alert))
    except Exception as e:
        print(f"[!] Graph alert handler error: {e}")

# Initialize packet processor
packet_procsr = PacketProcessor(analysis_callback=robust_analysis_pipeline)

# Network interface detection
import platform
import psutil

def get_default_interface():
    """Get the default network interface for the current system."""
    try:
        if platform.system() == "Windows":
            interfaces = psutil.net_if_addrs()
            for interface_name, addresses in interfaces.items():
                if 'Loopback' not in interface_name and 'VMware' not in interface_name:
                    for addr in addresses:
                        if addr.family == 2:  # AF_INET (IPv4)
                            return interface_name
            return 'Wi-Fi'
        else:
            return 'eth0'
    except Exception as e:
        print(f"[!] Interface detection error: {e}")
        return 'eth0'

default_interface = get_default_interface()
print(f"[*] Using network interface: {default_interface}")

# Initialize traffic sniffer
traffic_snffr = TrafficSniffer(
    interface=default_interface, 
    packet_callback=packet_procsr.process_packet
)

# Include authentication routes
app.include_router(auth_router, tags=["Authentication"])

# --- API Endpoints ---

@app.get("/", summary="API Status")
async def root():
    """API status and information"""
    return {
        "status": "running",
        "service": "Robust Dynamic Graph-Based NIDS",
        "version": "2.1.0",
        "ml_mode": ML_MODE,
        "robust_ml": ROBUST_ML_AVAILABLE,
        "components": {
            "traffic_sniffer": "initialized",
            "packet_processor": "initialized", 
            "ml_services": ML_MODE,
            "graph_manager": "initialized",
            "graph_analyzer": "initialized"
        }
    }

@app.get("/api/status", summary="System Status")
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Get detailed system status"""
    status = {
        "system": {
            "status": "running",
            "interface": default_interface,
            "ml_mode": ML_MODE
        },
        "connections": connection_manager.stats,
        "graph": {
            "nodes": len(graph_mgr.graph.nodes()),
            "edges": len(graph_mgr.graph.edges())
        }
    }
    
    # Add ML status if available
    if ml_services and hasattr(ml_services, 'get_model_info'):
        try:
            status["ml_services"] = ml_services.get_model_info()
        except Exception as e:
            status["ml_services"] = {"error": str(e), "available": False}
    else:
        status["ml_services"] = {"available": False, "mode": ML_MODE}
    
    return status

@app.get("/api/ml/status", summary="ML Services Status")
async def get_ml_status(current_user: dict = Depends(get_current_user)):
    """Get ML services status"""
    if ml_services and hasattr(ml_services, 'get_model_info'):
        try:
            return ml_services.get_model_info()
        except Exception as e:
            return {"error": str(e), "available": False}
    else:
        return {
            "available": False,
            "mode": ML_MODE,
            "message": "ML services not available in current configuration"
        }

@app.get("/api/ml/feature-importance", summary="Get Feature Importance")
async def get_feature_importance(current_user: dict = Depends(get_current_user)):
    """Get feature importance from ML models"""
    if ml_services and hasattr(ml_services, 'get_feature_importance'):
        try:
            importance = ml_services.get_feature_importance()
            if importance:
                return importance
        except Exception as e:
            return {"error": str(e)}
    
    raise HTTPException(status_code=404, detail="Feature importance not available")

@app.get("/api/graph/data", summary="Get Graph Data")
async def get_graph_data(current_user: dict = Depends(get_current_user)):
    """Get current network graph data"""
    try:
        nodes = []
        edges = []
        
        for node in graph_mgr.graph.nodes(data=True):
            nodes.append({
                "id": node[0],
                "data": node[1]
            })
        
        for edge in graph_mgr.graph.edges(data=True):
            edges.append({
                "source": edge[0],
                "target": edge[1],
                "data": edge[2]
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph data error: {str(e)}")

@app.post("/api/test/ml", summary="Test ML Prediction")
async def test_ml_prediction(current_user: dict = Depends(get_current_user)):
    """Test ML prediction with sample data"""
    if not ml_services:
        raise HTTPException(status_code=404, detail="ML services not available")
    
    # Sample feature vector for testing
    test_features = {
        'packet_length': 1500,
        'tcp_flags': 49,
        'src_port': 1337,
        'dst_port': 4444,
        'protocol': 6,
        'src_addr': '192.168.1.100',
        'dst_addr': '10.0.0.1'
    }
    
    try:
        if hasattr(ml_services, 'predict_anomaly'):
            result = await ml_services.predict_anomaly(test_features)
        elif hasattr(ml_services, 'predict'):
            result = await ml_services.predict(test_features)
        else:
            result = {"error": "No predict method available"}
        
        return {
            "test_features": test_features,
            "prediction": result,
            "ml_mode": ML_MODE
        }
    except Exception as e:
        return {
            "test_features": test_features,
            "error": str(e),
            "ml_mode": ML_MODE
        }

# --- WebSocket Endpoint ---
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await connection_manager.connect(websocket)
    try:
        # Send initial status
        status_message = {
            "type": "system_status",
            "message": "Connected to Robust NIDS WebSocket",
            "ml_mode": ML_MODE,
            "robust_ml": ROBUST_ML_AVAILABLE,
            "timestamp": "N/A"
        }
        await websocket.send_text(json.dumps(status_message))
        
        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                client_message = json.loads(data)
                if client_message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "keepalive"}))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"[!] WebSocket error: {e}")
        connection_manager.disconnect(websocket)

# --- Startup Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("🚀 Robust NIDS Starting Up")
    print("=" * 60)
    print(f"📡 Network Interface: {default_interface}")
    print(f"🤖 ML Mode: {ML_MODE}")
    print(f"🔧 Robust ML: {ROBUST_ML_AVAILABLE}")
    print(f"📊 Graph Analysis: Enabled")
    print(f"🔐 Authentication: Enabled")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🛑 Robust NIDS Shutting Down...")
    print("👋 Goodbye!")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Robust NIDS Backend")
    print("="*60)
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📍 WebSocket Alerts: ws://localhost:8000/ws/alerts")
    print("📍 Press Ctrl+C to stop the server")
    print("="*60)
    
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
