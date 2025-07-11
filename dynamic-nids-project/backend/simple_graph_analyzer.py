# backend/simple_graph_analyzer.py - Graph analysis without NetworkX dependencies

import asyncio
import time
import math
from collections import defaultdict

class SimpleGraphAnalyzer:
    """
    Graph analysis using basic algorithms without NetworkX dependency.
    """
    
    def __init__(self, graph_manager):
        self.gm = graph_manager
        self.node_history = defaultdict(list)  # Track node activity over time
        self.analysis_count = 0
    
    async def run_analysis_periodically(self, alert_callback):
        """Run graph analysis every 20 seconds"""
        while True:
            await asyncio.sleep(20)
            
            graph_data = self.gm.get_graph_data()
            if len(graph_data['nodes']) < 3:
                continue
                
            print(f"[*] Running graph analysis on {len(graph_data['nodes'])} nodes...")
            alerts = await self._analyze_network_patterns(graph_data)
            
            for alert in alerts:
                await alert_callback(alert)
    
    async def _analyze_network_patterns(self, graph_data):
        """Analyze network patterns and detect anomalies"""
        alerts = []
        nodes = graph_data['nodes']
        links = graph_data['links']
        
        # Create adjacency information
        adjacency = defaultdict(set)
        node_degrees = defaultdict(int)
        
        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('weight', 1)
            
            adjacency[source].add(target)
            adjacency[target].add(source)
            node_degrees[source] += weight
            node_degrees[target] += weight
        
        # 1. Detect high-degree nodes (potential hubs or attack targets)
        if node_degrees:
            avg_degree = sum(node_degrees.values()) / len(node_degrees)
            high_threshold = avg_degree * 3
            
            for node_id, degree in node_degrees.items():
                if degree > high_threshold and degree > 5:
                    # Check if this is a sudden increase
                    if self._is_sudden_increase(node_id, degree):
                        alerts.append({
                            'type': 'HighDegreeNode',
                            'node': node_id,
                            'metric': 'Degree',
                            'value': degree,
                            'threshold': high_threshold,
                            'message': f"Node {node_id} has unusually high connectivity (degree: {degree})"
                        })
        
        # 2. Detect isolated communication patterns
        isolated_pairs = self._find_isolated_pairs(adjacency, nodes)
        for pair in isolated_pairs:
            alerts.append({
                'type': 'IsolatedCommunication',
                'nodes': pair,
                'message': f"Isolated communication detected between {pair[0]} and {pair[1]}"
            })
        
        # 3. Detect potential scanning behavior
        scanning_nodes = self._detect_scanning_behavior(adjacency, links)
        for node in scanning_nodes:
            alerts.append({
                'type': 'PotentialScan',
                'node': node,
                'message': f"Node {node} shows potential scanning behavior"
            })
        
        # 4. Detect bridge nodes (nodes connecting different clusters)
        bridge_nodes = self._find_bridge_nodes(adjacency)
        for node in bridge_nodes:
            if node_degrees[node] > 3:  # Only alert for significant bridges
                alerts.append({
                    'type': 'BridgeNode',
                    'node': node,
                    'message': f"Node {node} acts as a bridge between network segments"
                })
        
        return alerts
    
    def _is_sudden_increase(self, node_id, current_degree):
        """Check if node degree increased suddenly"""
        history = self.node_history[node_id]
        history.append((time.time(), current_degree))
        
        # Keep only recent history (last 5 measurements)
        history = history[-5:]
        self.node_history[node_id] = history
        
        if len(history) < 3:
            return False
        
        # Check if current degree is significantly higher than previous
        prev_degrees = [degree for _, degree in history[:-1]]
        avg_prev = sum(prev_degrees) / len(prev_degrees)
        
        return current_degree > avg_prev * 2 and current_degree > 5
    
    def _find_isolated_pairs(self, adjacency, nodes):
        """Find pairs of nodes that only communicate with each other"""
        isolated_pairs = []
        
        for node in nodes:
            node_id = node['id']
            neighbors = adjacency[node_id]
            
            # If node has exactly one neighbor, check if it's mutual isolation
            if len(neighbors) == 1:
                neighbor = list(neighbors)[0]
                if len(adjacency[neighbor]) == 1:
                    pair = tuple(sorted([node_id, neighbor]))
                    if pair not in isolated_pairs:
                        isolated_pairs.append(pair)
        
        return isolated_pairs
    
    def _detect_scanning_behavior(self, adjacency, links):
        """Detect nodes that connect to many different nodes with low traffic"""
        scanning_nodes = []
        
        # Count connections per node
        connection_counts = defaultdict(int)
        connection_weights = defaultdict(list)
        
        for link in links:
            source = link['source']
            target = link['target']
            weight = link.get('weight', 1)
            
            connection_counts[source] += 1
            connection_counts[target] += 1
            connection_weights[source].append(weight)
            connection_weights[target].append(weight)
        
        for node, count in connection_counts.items():
            if count >= 4:  # Connected to 4+ different nodes
                weights = connection_weights[node]
                avg_weight = sum(weights) / len(weights) if weights else 0
                
                # Low average weight suggests scanning (many connections, little data)
                if avg_weight <= 2:
                    scanning_nodes.append(node)
        
        return scanning_nodes
    
    def _find_bridge_nodes(self, adjacency):
        """Simple bridge detection - nodes that connect otherwise disconnected components"""
        bridge_nodes = []
        
        for node in adjacency:
            neighbors = list(adjacency[node])
            
            if len(neighbors) >= 2:
                # Check if removing this node would disconnect its neighbors
                # Simple approach: check if neighbors are connected to each other
                neighbor_connections = 0
                for i in range(len(neighbors)):
                    for j in range(i + 1, len(neighbors)):
                        if neighbors[j] in adjacency[neighbors[i]]:
                            neighbor_connections += 1
                
                # If neighbors aren't well connected, this might be a bridge
                max_possible_connections = len(neighbors) * (len(neighbors) - 1) // 2
                if neighbor_connections < max_possible_connections * 0.3:
                    bridge_nodes.append(node)
        
        return bridge_nodes

class EnhancedGraphManager:
    """Enhanced graph manager with time-based pruning and better analytics"""
    
    def __init__(self, ttl=300):
        self.nodes = {}
        self.links = []
        self.ttl = ttl
        self.last_prune = time.time()
    
    def add_node(self, node_id):
        current_time = time.time()
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "packet_count": 1,
                "first_seen": current_time,
                "last_seen": current_time
            }
        else:
            self.nodes[node_id]["packet_count"] += 1
            self.nodes[node_id]["last_seen"] = current_time
    
    def add_edge(self, source, target):
        current_time = time.time()
        
        # Find existing edge
        for link in self.links:
            if (link["source"] == source and link["target"] == target) or \
               (link["source"] == target and link["target"] == source):
                link["weight"] += 1
                link["last_seen"] = current_time
                return
        
        # Add new edge
        self.links.append({
            "source": source,
            "target": target,
            "weight": 1,
            "first_seen": current_time,
            "last_seen": current_time
        })
    
    def prune_old_data(self):
        """Remove old nodes and edges"""
        current_time = time.time()
        
        # Prune old links
        self.links = [link for link in self.links 
                     if current_time - link.get("last_seen", 0) <= self.ttl]
        
        # Prune isolated nodes
        active_nodes = set()
        for link in self.links:
            active_nodes.add(link["source"])
            active_nodes.add(link["target"])
        
        # Keep nodes that are either active in links or recently seen
        self.nodes = {node_id: data for node_id, data in self.nodes.items()
                     if node_id in active_nodes or 
                     current_time - data.get("last_seen", 0) <= self.ttl}
    
    def get_graph_data(self):
        # Auto-prune if needed
        if time.time() - self.last_prune > 60:  # Prune every minute
            self.prune_old_data()
            self.last_prune = time.time()
        
        return {
            "nodes": list(self.nodes.values()),
            "links": self.links
        }
