# backend/graph_analyzer.py

import networkx as nx
from sklearn.cluster import DBSCAN
import numpy as np
import asyncio

class GraphAnalyzer:
    """
    Performs advanced analysis on the network graph to find anomalous patterns.
    """
    def __init__(self, graph_manager):
        """
        Initializes the Graph Analyzer.
        
        Args:
            graph_manager (GraphManager): An instance of the GraphManager.
        """
        self.gm = graph_manager
        # Store the history of centrality scores to detect significant shifts over time.
        self.centrality_history = {}
        self.lock = asyncio.Lock()

    async def run_analysis_periodically(self, alert_callback):
        """
        Runs a continuous loop to perform graph analysis at regular intervals.
        
        Args:
            alert_callback (callable): An awaitable function to send generated alerts to.
        """
        while True:
            await asyncio.sleep(15) # Run analysis every 15 seconds
            async with self.lock:
                graph_size = self.gm.graph.number_of_nodes()
                if graph_size < 5: # Don't run on a trivial graph
                    continue

                print(f"[*] Running graph analysis on {graph_size} nodes...")
                centrality_alerts = await self._analyze_centrality_shifts()
                cluster_alerts = await self._analyze_traffic_clusters()
                
                all_alerts = centrality_alerts + cluster_alerts
                for alert in all_alerts:
                    await alert_callback(alert)

    async def _analyze_centrality_shifts(self):
        """
        Calculates centrality measures and detects anomalous shifts from historical values.
        Centrality algorithms are key for finding influential or suspicious nodes.
        """
        graph = self.gm.graph
        alerts = []
        
        try:
            # Calculate current centrality scores
            degree_centrality = nx.degree_centrality(graph)
            betweenness_centrality = nx.betweenness_centrality(graph, k=min(100, len(graph.nodes)-1)) # Use a sample for performance

            for node in graph.nodes():
                # --- Check for Betweenness Centrality Spike (potential MitM or bridge) ---
                prev_bc = self.centrality_history.get(node, {}).get('betweenness', 0)
                curr_bc = betweenness_centrality.get(node, 0)
                
                # Rule: Alert if centrality more than quintuples and exceeds a baseline threshold.
                if curr_bc > 0.1 and curr_bc > prev_bc * 5 and prev_bc > 0:
                    alerts.append({
                        'type': 'CentralityShift',
                        'node': node,
                        'metric': 'Betweenness',
                        'old_value': round(prev_bc, 4),
                        'new_value': round(curr_bc, 4),
                        'message': f"Anomalous spike in Betweenness Centrality for node {node}."
                    })
                
                # Update history for the node
                if node not in self.centrality_history:
                    self.centrality_history[node] = {}
                self.centrality_history[node]['betweenness'] = curr_bc
                self.centrality_history[node]['degree'] = degree_centrality.get(node, 0)

        except Exception as e:
            print(f"[!] Error during centrality analysis: {e}")
            
        return alerts

    async def _analyze_traffic_clusters(self):
        """
        Uses DBSCAN clustering on the graph's topology to find outlier nodes.
        Clustering can reveal hosts communicating in unusual patterns.
        """
        graph = self.gm.graph
        alerts = []
        
        try:
            # Use node positions from a force-directed layout as features for spatial clustering.
            # This converts topological relationships into a 2D space.
            pos = nx.spring_layout(graph, iterations=50) 
            node_points = np.array([pos[node] for node in graph.nodes()])
            
            # DBSCAN groups together points that are closely packed, marking as outliers
            # points that lie alone in low-density regions.
            clustering = DBSCAN(eps=0.3, min_samples=3).fit(node_points)
            labels = clustering.labels_
            
            # Identify noise points (outliers), which are assigned the label -1 by DBSCAN.
            outlier_indices = np.where(labels == -1)[0]
            all_nodes = list(graph.nodes())
            outlier_nodes = [all_nodes[i] for i in outlier_indices]
            
            for node in outlier_nodes:
                alerts.append({
                    'type': 'TrafficClusterOutlier',
                    'node': node,
                    'message': f"Node {node} identified as a topological outlier by DBSCAN clustering."
                })
        except Exception as e:
            print(f"[!] Error during cluster analysis: {e}")

        return alerts
