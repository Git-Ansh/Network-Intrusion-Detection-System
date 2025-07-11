# backend/main_minimal.py - No authentication version for immediate testing

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import random

# --- Application Setup ---
app = FastAPI(
    title="Dynamic Graph-Based NIDS API",
    description="Provides real-time network graph data and security alerts.",
    version="1.0.0"
)

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core Components ---
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
        for connection in self.active_connections[:]:  # Copy list to avoid modification during iteration
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

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
        for link in self.links:
            if (link["source"] == source and link["target"] == target) or \
               (link["source"] == target and link["target"] == source):
                link["weight"] += 1
                return
        
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

# Demo data generator
async def generate_demo_data():
    """Generate demo network data"""
    demo_ips = ["192.168.1.1", "192.168.1.10", "192.168.1.20", "10.0.0.1", "172.16.1.5", "8.8.8.8"]
    
    while True:
        await asyncio.sleep(3)  # Generate data every 3 seconds
        
        source = random.choice(demo_ips)
        target = random.choice(demo_ips)
        
        if source != target:
            graph_mgr.add_node(source)
            graph_mgr.add_node(target)
            graph_mgr.add_edge(source, target)
            
            # Generate alerts occasionally
            if random.random() < 0.15:  # 15% chance
                alert_types = ["Suspicious_Traffic", "Port_Scan", "Anomaly_Detected"]
                alert = {
                    "type": random.choice(alert_types),
                    "message": f"Alert: {random.choice(alert_types).replace('_', ' ')} detected between {source} and {target}",
                    "timestamp": time.time(),
                    "node": source,
                    "details": {
                        "src_addr": source,
                        "dst_addr": target,
                        "severity": random.choice(["Low", "Medium", "High"])
                    }
                }
                await connection_manager.broadcast(json.dumps(alert))

@app.on_event("startup")
async def startup_event():
    print("[*] NIDS API starting up...")
    print("[*] Demo data generator starting...")
    asyncio.create_task(generate_demo_data())

@app.get("/")
async def root():
    return {
        "status": "NIDS API is running",
        "version": "1.0.0",
        "mode": "demo - no authentication",
        "nodes": len(graph_mgr.nodes),
        "links": len(graph_mgr.links)
    }

@app.get("/api/graph")
async def get_graph_data():
    """Get network graph data - no authentication required"""
    return graph_mgr.get_graph_data()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time alerts"""
    await connection_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        print("[*] WebSocket client disconnected")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
