# backend/main_simple.py - Simplified version without ML dependencies

from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import random

from auth_simple import router as auth_router, get_current_user

# --- Application Setup ---
app = FastAPI(
    title="Dynamic Graph-Based NIDS API",
    description="Provides real-time network graph data and security alerts.",
    version="1.0.0"
)

# Allow the frontend (running on localhost:3000) to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                pass

# Simple graph manager without NetworkX
class SimpleGraphManager:
    def __init__(self):
        self.nodes = {}
        self.links = []
        
    def add_node(self, node_id):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "packet_count": 1,
                "last_seen": time.time()
            }
        else:
            self.nodes[node_id]["packet_count"] += 1
            self.nodes[node_id]["last_seen"] = time.time()
    
    def add_edge(self, source, target):
        # Find existing edge
        for link in self.links:
            if (link["source"] == source and link["target"] == target) or \
               (link["source"] == target and link["target"] == source):
                link["weight"] += 1
                return
        
        # Add new edge
        self.links.append({
            "source": source,
            "target": target,
            "weight": 1
        })
    
    def get_graph_data(self):
        return {
            "nodes": list(self.nodes.values()),
            "links": self.links
        }

# Instantiate components
connection_manager = ConnectionManager()
graph_mgr = SimpleGraphManager()

# Include the authentication routes (e.g., /token)
app.include_router(auth_router, tags=["Authentication"])

# Demo data generator
async def generate_demo_data():
    """Generate demo network data for visualization"""
    demo_ips = ["192.168.1.1", "192.168.1.10", "192.168.1.20", "10.0.0.1", "172.16.1.5"]
    
    while True:
        await asyncio.sleep(2)  # Generate data every 2 seconds
        
        # Add random nodes and connections
        source = random.choice(demo_ips)
        target = random.choice(demo_ips)
        
        if source != target:
            graph_mgr.add_node(source)
            graph_mgr.add_node(target)
            graph_mgr.add_edge(source, target)
            
            # Occasionally generate an alert
            if random.random() < 0.1:  # 10% chance
                alert = {
                    "type": "Demo_Alert",
                    "message": f"Demo: Suspicious activity between {source} and {target}",
                    "timestamp": time.time(),
                    "node": source
                }
                await connection_manager.broadcast(json.dumps(alert))

# --- Background Tasks ---
@app.on_event("startup")
async def startup_event():
    """
    On application startup, launch the demo data generator.
    """
    print("[*] Application startup: launching demo data generator...")
    asyncio.create_task(generate_demo_data())

# --- API Endpoints ---
@app.get("/api/graph", summary="Get the current network graph")
async def get_graph_data(current_user: dict = Depends(get_current_user)):
    """
    Provides the current network graph data in a D3.js-compatible format.
    This endpoint is protected and requires a valid JWT token.
    """
    return graph_mgr.get_graph_data()

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

@app.get("/", summary="API Status")
async def root():
    """Basic API status endpoint"""
    return {
        "status": "NIDS API is running",
        "version": "1.0.0",
        "mode": "demo",
        "nodes": len(graph_mgr.nodes),
        "links": len(graph_mgr.links)
    }
