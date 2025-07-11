# backend/simple_detector_nonumpy.py

"""
Simple anomaly detector without numpy dependency
Pure Python implementation for Windows compatibility
"""

import json
import random
import time
import math

class SimpleAnomalyDetector:
    """
    A simplified anomaly detector that works without any ML dependencies.
    Uses statistical methods and rule-based detection.
    """
    
    def __init__(self):
        self.packet_history = []
        self.baseline_stats = {
            'avg_packet_size': 500,
            'std_packet_size': 200,
            'common_ports': {80, 443, 22, 53, 25, 110, 143, 993, 995},
            'suspicious_ports': {1337, 4444, 6666, 31337, 12345}
        }
        print("[*] Simple Anomaly Detector initialized (no dependencies)")
    
    async def predict(self, feature_vector):
        """
        Analyze a packet and return anomaly prediction using simple rules.
        
        Args:
            feature_vector (dict): Packet features
            
        Returns:
            dict: Prediction results
        """
        if not feature_vector:
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'confidence': 0.0,
                'reasoning': ['No data provided']
            }
            
        # Store packet for statistical analysis
        self.packet_history.append(feature_vector)
        if len(self.packet_history) > 1000:  # Keep only recent packets
            self.packet_history = self.packet_history[-1000:]
        
        # Rule-based anomaly detection
        anomaly_score = 0
        anomaly_reasons = []
        
        # 1. Check packet size anomalies
        packet_size = feature_vector.get('packet_length', feature_vector.get('packet_size', 0))
        if packet_size > 1400:  # Unusually large packet
            anomaly_score += 0.3
            anomaly_reasons.append("Large packet size")
        elif packet_size > 0 and packet_size < 64:  # Suspiciously small
            anomaly_score += 0.2
            anomaly_reasons.append("Small packet size")
        
        # 2. Check port anomalies
        port = feature_vector.get('port', feature_vector.get('dst_port', 0))
        if port in self.baseline_stats['suspicious_ports']:
            anomaly_score += 0.4
            anomaly_reasons.append(f"Suspicious port {port}")
        elif port > 49152:  # High dynamic/private ports
            anomaly_score += 0.1
            anomaly_reasons.append("High port number")
        
        # 3. Check protocol anomalies
        protocol = feature_vector.get('protocol', '').upper()
        if protocol in ['ICMP', 'IGMP']:
            anomaly_score += 0.2
            anomaly_reasons.append(f"Unusual protocol {protocol}")
        
        # 4. Check timing anomalies
        time_delta = feature_vector.get('time_delta', 0)
        if time_delta > 0 and time_delta < 0.001:  # Very fast succession
            anomaly_score += 0.2
            anomaly_reasons.append("High frequency traffic")
        
        # 5. Check for scanning patterns
        if self._detect_port_scan(feature_vector):
            anomaly_score += 0.5
            anomaly_reasons.append("Port scan detected")
        
        # Normalize score
        anomaly_score = min(anomaly_score, 1.0)
        is_anomaly = anomaly_score > 0.5
        
        # Generate confidence based on available features
        available_features = sum(1 for v in feature_vector.values() if v is not None)
        confidence = min(available_features / 5.0, 1.0)  # More features = higher confidence
        
        result = {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(anomaly_score, 3),
            'confidence': round(confidence, 3),
            'reasoning': anomaly_reasons if anomaly_reasons else ['Normal traffic pattern'],
            'detector_type': 'rule_based',
            'features_analyzed': list(feature_vector.keys())
        }
        
        return result
    
    def _detect_port_scan(self, feature_vector):
        """Detect potential port scanning activity"""
        if len(self.packet_history) < 10:
            return False
        
        # Check for multiple different destination ports from same source
        recent_packets = self.packet_history[-10:]
        src_ip = feature_vector.get('src_ip', '')
        
        if not src_ip:
            return False
        
        # Count unique destination ports from this source
        ports = set()
        for packet in recent_packets:
            if packet.get('src_ip') == src_ip:
                port = packet.get('port', packet.get('dst_port'))
                if port:
                    ports.add(port)
        
        # If more than 5 different ports in recent history, likely scanning
        return len(ports) > 5
    
    def update_baseline(self, packets):
        """Update baseline statistics from a set of packets"""
        if not packets:
            return
        
        # Calculate new averages
        sizes = [p.get('packet_length', p.get('packet_size', 0)) for p in packets if p.get('packet_length') or p.get('packet_size')]
        if sizes:
            self.baseline_stats['avg_packet_size'] = sum(sizes) / len(sizes)
            # Simple standard deviation calculation
            variance = sum((x - self.baseline_stats['avg_packet_size']) ** 2 for x in sizes) / len(sizes)
            self.baseline_stats['std_packet_size'] = math.sqrt(variance)
        
        print(f"[*] Updated baseline: avg_size={self.baseline_stats['avg_packet_size']:.0f}, std={self.baseline_stats['std_packet_size']:.0f}")
    
    def get_stats(self):
        """Get detector statistics"""
        return {
            'packets_analyzed': len(self.packet_history),
            'baseline_stats': self.baseline_stats,
            'detector_type': 'simple_rule_based'
        }
