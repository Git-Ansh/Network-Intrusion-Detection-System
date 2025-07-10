# backend/main.py

from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from sniffer import TrafficSniffer
from processor import PacketProcessor
from detector import AnomalyDetector
from graph_manager import GraphManager
from graph_analyzer import GraphAnalyzer
from auth import router as auth_router, get_current_user

# --- Application Setup ---
app = FastAPI(
    title="Dynamic Graph-Based NIDS API",
    description="Provides real-time network graph data and security alerts.",
    version="1.0.0"
)

# Allow the frontend (running on localhost:3000) to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core Components Initialization ---
# This class manages active WebSocket connections for broadcasting alerts.
class ConnectionManager:
    def __init__(self):
        self.active_connections: list = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Instantiate all system components
connection_manager = ConnectionManager()
graph_mgr = GraphManager(ttl=300)
graph_anlyzr = GraphAnalyzer(graph_mgr)
anomaly_dtctr = AnomalyDetector()

# Define the main analysis pipeline callback
async def analysis_pipeline(feature_vector):
    # This function is called by the processor for each packet
    ml_results = await anomaly_dtctr.predict(feature_vector)
    await graph_mgr.update_graph(feature_vector, ml_results)
    if ml_results and ml_results['is_anomaly']:
        alert = {
            "type": "ML_Anomaly",
            "message": f"Potential anomaly detected from {feature_vector['src_addr']} to {feature_vector['dst_addr']}",
            "details": {**feature_vector, **ml_results}
        }
        await connection_manager.broadcast(json.dumps(alert))

async def alert_handler(alert):
    # This function is called by the graph analyzer
    await connection_manager.broadcast(json.dumps(alert))

packet_procsr = PacketProcessor(analysis_callback=analysis_pipeline)

# Auto-detect network interface for Windows/cross-platform compatibility
import platform
import psutil

def get_default_interface():
    """Get the default network interface for the current system."""
    try:
        if platform.system() == "Windows":
            # On Windows, try to find an active ethernet or Wi-Fi interface
            interfaces = psutil.net_if_addrs()
            for interface_name, addresses in interfaces.items():
                if 'Loopback' not in interface_name and 'VMware' not in interface_name:
                    for addr in addresses:
                        if addr.family == 2:  # AF_INET (IPv4)
                            return interface_name
            return 'Wi-Fi'  # Fallback for Windows
        else:
            # Unix-like systems
            return 'eth0'
    except:
        return 'eth0'  # Ultimate fallback

default_interface = get_default_interface()
print(f"[*] Using network interface: {default_interface}")
traffic_snffr = TrafficSniffer(interface=default_interface, packet_callback=packet_procsr.process_packet)

# Include the authentication routes (e.g., /token)
app.include_router(auth_router, tags=["Authentication"])

# --- Background Tasks ---
@app.on_event("startup")
async def startup_event():
    """
    On application startup, launch the long-running background tasks.
    """
    print("[*] Application startup: launching background tasks...")
    asyncio.create_task(traffic_snffr.start_sniffing())
    asyncio.create_task(graph_mgr.prune_graph_periodically())
    asyncio.create_task(graph_anlyzr.run_analysis_periodically(alert_callback=alert_handler))

# --- API Endpoints ---
@app.get("/api/graph", summary="Get the current network graph")
async def get_graph_data(current_user: dict = Depends(get_current_user)):
    """
    Provides the current network graph data in a D3.js-compatible format.
    This endpoint is protected and requires a valid JWT token.
    """
    return await graph_mgr.get_graph_json()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    Establishes a WebSocket connection for streaming real-time security alerts.
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        print(f"[*] WebSocket client disconnected.")
