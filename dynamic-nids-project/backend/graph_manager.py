# backend/graph_manager.py

import networkx as nx
import time
import asyncio

class GraphManager:
    """
    Manages the state of the dynamic network graph using NetworkX.
    This class handles the creation, updating, and pruning of nodes and edges.
    """
    def __init__(self, ttl=300):
        """
        Initializes the Graph Manager.
        
        Args:
            ttl (int): Time-to-live in seconds. Nodes and edges not seen within
                       this duration will be pruned from the graph.
        """
        self.graph = nx.Graph()
        self.ttl = ttl
        self.lock = asyncio.Lock() # To prevent race conditions during graph updates

    async def update_graph(self, feature_vector, ml_results=None):
        """
        Updates the graph with data from a new packet and its analysis results.
        This method is the primary entry point for modifying the graph's state.
        
        Args:
            feature_vector (dict): The structured data from the PacketProcessor.
            ml_results (dict, optional): The anomaly scores from the AnomalyDetector.
        """
        src_ip = feature_vector['src_addr']
        dst_ip = feature_vector['dst_addr']
        current_time = feature_vector['timestamp']
        
        async with self.lock:
            # Add or update source and destination nodes
            for node_ip in [src_ip, dst_ip]:
                if self.graph.has_node(node_ip):
                    self.graph.nodes[node_ip]['last_seen'] = current_time
                    self.graph.nodes[node_ip]['packet_count'] += 1
                else:
                    self.graph.add_node(node_ip, last_seen=current_time, packet_count=1, first_seen=current_time)

            # Add or update the edge between the nodes
            if self.graph.has_edge(src_ip, dst_ip):
                self.graph[src_ip][dst_ip]['weight'] += 1
                self.graph[src_ip][dst_ip]['last_seen'] = current_time
            else:
                self.graph.add_edge(src_ip, dst_ip, weight=1, last_seen=current_time)
            
            # The NetworkX Graph.update method is also an option for bulk updates
            # but per-packet updates are more suitable for this real-time model.

    async def prune_graph_periodically(self):
        """
        Runs a continuous loop to periodically prune old nodes and edges.
        """
        while True:
            await asyncio.sleep(self.ttl / 2) # Prune at half the TTL interval
            async with self.lock:
                current_time = time.time()
                
                # Identify and remove old edges
                old_edges = [(u, v) for u, v, data in self.graph.edges(data=True) 
                            if current_time - data['last_seen'] > self.ttl]
                if old_edges:
                    self.graph.remove_edges_from(old_edges)
                    print(f"[*] Pruned {len(old_edges)} old edges.")

                # Identify and remove old nodes that are now isolated
                old_nodes = [node for node, data in self.graph.nodes(data=True) 
                            if current_time - data['last_seen'] > self.ttl and self.graph.degree(node) == 0]
                if old_nodes:
                    self.graph.remove_nodes_from(old_nodes)
                    print(f"[*] Pruned {len(old_nodes)} isolated nodes.")

    async def get_graph_json(self):
        """
        Returns a JSON-serializable representation of the graph for API consumption.
        The format is compatible with D3.js force-directed layouts.
        
        Returns:
            dict: A dictionary in node-link format.
        """
        async with self.lock:
            # node_link_data is a standard format for graph serialization
            return nx.node_link_data(self.graph)
