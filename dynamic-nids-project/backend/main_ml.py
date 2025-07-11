# backend/main_ml.py

"""
Enhanced FastAPI backend with integrated ML services
Provides adaptive ML functionality with fallbacks
"""

from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from typing import List

from sniffer import TrafficSniffer
from processor import PacketProcessor
from graph_manager import GraphManager
from graph_analyzer import GraphAnalyzer
from auth import router as auth_router, get_current_user
from ml_services import get_ml_services, get_model_status

# --- Application Setup ---
app = FastAPI(
    title="Dynamic Graph-Based NIDS API with ML Services",
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
            'messages_sent': 0
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.stats['total_connections'] += 1
        self.stats['active_connections'] = len(self.active_connections)
        print(f"[*] WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.stats['active_connections'] = len(self.active_connections)
        print(f"[*] WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                    self.stats['messages_sent'] += 1
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

# --- Core Components Initialization ---
connection_manager = ConnectionManager()
graph_mgr = GraphManager(ttl=300)
graph_anlyzr = GraphAnalyzer(graph_mgr)
ml_services = get_ml_services()

# Enhanced analysis pipeline with ML services
async def enhanced_analysis_pipeline(feature_vector):
    """
    Enhanced analysis pipeline that integrates ML services
    """
    try:
        # 1. ML-based anomaly detection
        ml_results = await ml_services.predict_anomaly(feature_vector)
        
        # 2. Update graph with ML results
        await graph_mgr.update_graph(feature_vector, ml_results)
        
        # 3. Graph-based analysis
        graph_alerts = await graph_anlyzr.analyze()
        
        # 4. Handle ML anomalies
        if ml_results and ml_results.get('is_anomaly'):
            alert = {
                "type": "ML_Anomaly",
                "timestamp": feature_vector.get('timestamp'),
                "severity": "HIGH" if ml_results.get('confidence', 0) > 0.8 else "MEDIUM",
                "message": f"ML-detected anomaly: {feature_vector['src_addr']} → {feature_vector['dst_addr']}",
                "details": {
                    "packet_info": {
                        "src_addr": feature_vector['src_addr'],
                        "dst_addr": feature_vector['dst_addr'],
                        "src_port": feature_vector.get('src_port'),
                        "dst_port": feature_vector.get('dst_port'),
                        "protocol": feature_vector.get('protocol'),
                        "packet_length": feature_vector.get('packet_length')
                    },
                    "ml_prediction": ml_results,
                    "feature_vector": feature_vector
                }
            }
            await connection_manager.broadcast(json.dumps(alert))
        
        # 5. Handle graph-based alerts
        for alert in graph_alerts:
            await connection_manager.broadcast(json.dumps(alert))
            
    except Exception as e:
        logging.error(f"Error in enhanced analysis pipeline: {e}")

# Alert handler for graph analyzer
async def alert_handler(alert):
    await connection_manager.broadcast(json.dumps(alert))

# Initialize packet processor with enhanced pipeline
packet_procsr = PacketProcessor(analysis_callback=enhanced_analysis_pipeline)

# Auto-detect network interface
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
    except:
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
        "service": "Dynamic Graph-Based NIDS with ML Services",
        "version": "2.0.0",
        "ml_enabled": ml_services.ml_available,
        "components": {
            "traffic_sniffer": "initialized",
            "packet_processor": "initialized", 
            "ml_services": "initialized",
            "graph_manager": "initialized",
            "graph_analyzer": "initialized"
        }
    }

@app.get("/api/status", summary="System Status")
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Get detailed system status (protected endpoint)"""
    return {
        "system": {
            "status": "running",
            "uptime": "N/A",  # You can implement uptime tracking
            "interface": default_interface
        },
        "ml_services": ml_services.get_model_info(),
        "graph": {
            "nodes": len(graph_mgr.graph.nodes()),
            "edges": len(graph_mgr.graph.edges()),
            "last_updated": "N/A"  # You can implement timestamp tracking
        },
        "connections": connection_manager.stats
    }

@app.get("/api/ml/status", summary="ML Services Status")
async def get_ml_status(current_user: dict = Depends(get_current_user)):
    """Get ML services status and model information"""
    return get_model_status()

@app.get("/api/ml/feature-importance", summary="Get Feature Importance")
async def get_feature_importance(current_user: dict = Depends(get_current_user)):
    """Get feature importance from ML models"""
    importance = ml_services.get_feature_importance()
    if not importance:
        raise HTTPException(status_code=404, detail="Feature importance not available")
    return importance

@app.post("/api/ml/retrain", summary="Retrain ML Models")
async def retrain_models(current_user: dict = Depends(get_current_user)):
    """Trigger model retraining"""
    try:
        success = await ml_services.train_models()
        if success:
            return {"status": "success", "message": "Models retrained successfully"}
        else:
            raise HTTPException(status_code=500, detail="Model training failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.get("/api/graph/data", summary="Get Graph Data")
async def get_graph_data(current_user: dict = Depends(get_current_user)):
    """Get current network graph data"""
    nodes = []
    edges = []
    
    # Convert NetworkX graph to JSON-serializable format
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

@app.post("/api/sniffer/start", summary="Start Traffic Capture")
async def start_traffic_capture(current_user: dict = Depends(get_current_user)):
    """Start network traffic capture"""
    try:
        if not traffic_snffr.is_running:
            asyncio.create_task(traffic_snffr.start_capture())
            return {"status": "started", "interface": default_interface}
        else:
            return {"status": "already_running", "interface": default_interface}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start capture: {str(e)}")

@app.post("/api/sniffer/stop", summary="Stop Traffic Capture")
async def stop_traffic_capture(current_user: dict = Depends(get_current_user)):
    """Stop network traffic capture"""
    try:
        await traffic_snffr.stop_capture()
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop capture: {str(e)}")

# --- WebSocket Endpoint ---
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts and graph updates"""
    await connection_manager.connect(websocket)
    try:
        # Send initial status
        status_message = {
            "type": "system_status",
            "message": "Connected to NIDS WebSocket",
            "ml_enabled": ml_services.ml_available,
            "timestamp": "N/A"
        }
        await websocket.send_text(json.dumps(status_message))
        
        # Keep connection alive and handle client messages
        while True:
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
    print("🚀 NIDS with ML Services Starting Up")
    print("=" * 60)
    print(f"📡 Network Interface: {default_interface}")
    print(f"🤖 ML Services: {'Advanced' if ml_services.ml_available else 'Simple'}")
    print(f"📊 Graph Analysis: Enabled")
    print(f"🔐 Authentication: Enabled")
    print("=" * 60)
    
    # Auto-start traffic capture
    try:
        asyncio.create_task(traffic_snffr.start_capture())
        print("✅ Traffic capture started automatically")
    except Exception as e:
        print(f"⚠️  Failed to auto-start traffic capture: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🛑 NIDS Shutting Down...")
    try:
        await traffic_snffr.stop_capture()
        print("✅ Traffic capture stopped")
    except:
        pass
    print("👋 Goodbye!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
