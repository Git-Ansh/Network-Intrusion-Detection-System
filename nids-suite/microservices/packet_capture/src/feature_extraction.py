#!/usr/bin/env python3
"""
Feature extraction module for the packet capture service.
Extracts network traffic features from packet captures for ML analysis.
"""

import os
import time
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import dpkt
import numpy as np
import scapy.all as scapy
from scapy.layers import http, tls
from scapy.packet import Packet

# Configure logging
logging.basicConfig(
    level=logging.INFO if not os.getenv('LOG_LEVEL') else os.getenv('LOG_LEVEL'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Extracts features from network flows and packets for machine learning analysis.
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        logger.debug("Feature extractor initialized")
    
    def extract_flow_features(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from a network flow.
        
        Args:
            flow: Dictionary containing flow information
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Basic flow statistics
            features['duration'] = (flow.get('end_time', 0) - flow.get('start_time', 0)) / 1000000  # μs to seconds
            features['bytes'] = flow.get('bytes', 0)
            features['packets'] = flow.get('packets', 0)
            
            # Derived metrics
            if features['duration'] > 0:
                features['bytes_per_second'] = features['bytes'] / features['duration']
                features['packets_per_second'] = features['packets'] / features['duration']
            else:
                features['bytes_per_second'] = features['bytes']  # For very short flows
                features['packets_per_second'] = features['packets']
                
            if features['packets'] > 0:
                features['bytes_per_packet'] = features['bytes'] / features['packets']
            else:
                features['bytes_per_packet'] = 0
            
            # Flag counts (if available)
            if 'tcp_flags' in flow:
                flags = flow['tcp_flags']
                features['syn_count'] = flags.get('syn', 0)
                features['ack_count'] = flags.get('ack', 0)
                features['fin_count'] = flags.get('fin', 0)
                features['rst_count'] = flags.get('rst', 0)
                features['psh_count'] = flags.get('psh', 0)
                features['urg_count'] = flags.get('urg', 0)
                
                # Flag ratios
                if features['packets'] > 0:
                    features['syn_ratio'] = features['syn_count'] / features['packets']
                    features['ack_ratio'] = features['ack_count'] / features['packets']
                    features['fin_ratio'] = features['fin_count'] / features['packets']
                    features['rst_ratio'] = features['rst_count'] / features['packets']
            
            # Port analysis
            src_port = flow.get('src_port', 0)
            dst_port = flow.get('dst_port', 0)
            features['src_port'] = src_port
            features['dst_port'] = dst_port
            features['is_well_known_port'] = 1 if (src_port < 1024 or dst_port < 1024) else 0
            
            # Service identification (common ports)
            features['is_http'] = 1 if (src_port == 80 or dst_port == 80) else 0
            features['is_https'] = 1 if (src_port == 443 or dst_port == 443) else 0
            features['is_dns'] = 1 if (src_port == 53 or dst_port == 53) else 0
            features['is_smtp'] = 1 if (src_port == 25 or dst_port == 25) else 0
            features['is_ssh'] = 1 if (src_port == 22 or dst_port == 22) else 0
            
            # Protocol specific features
            protocol = flow.get('protocol', '').lower()
            features['is_tcp'] = 1 if protocol == 'tcp' else 0
            features['is_udp'] = 1 if protocol == 'udp' else 0
            features['is_icmp'] = 1 if protocol == 'icmp' else 0
            
            # Add packet statistics if available
            if 'packet_sizes' in flow:
                packet_sizes = flow['packet_sizes']
                if packet_sizes:
                    features['min_packet_size'] = min(packet_sizes)
                    features['max_packet_size'] = max(packet_sizes)
                    features['mean_packet_size'] = statistics.mean(packet_sizes)
                    if len(packet_sizes) > 1:
                        features['std_packet_size'] = statistics.stdev(packet_sizes)
                    else:
                        features['std_packet_size'] = 0
            
            # Add inter-arrival time statistics if available
            if 'inter_arrival_times' in flow:
                iat = flow['inter_arrival_times']
                if iat:
                    features['min_iat'] = min(iat)
                    features['max_iat'] = max(iat)
                    features['mean_iat'] = statistics.mean(iat)
                    if len(iat) > 1:
                        features['std_iat'] = statistics.stdev(iat)
                    else:
                        features['std_iat'] = 0
            
            # Connection state
            if 'state' in flow:
                state = flow.get('state', '')
                features['is_established'] = 1 if state == 'established' else 0
                features['is_closed'] = 1 if state == 'closed' else 0
                features['is_reset'] = 1 if state == 'reset' else 0
                features['is_ongoing'] = 1 if state == 'ongoing' else 0
            
            logger.debug(f"Extracted {len(features)} features from flow {flow.get('flow_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error extracting features from flow: {str(e)}")
        
        return features
    
    def extract_packet_features(self, packet: Packet) -> Dict[str, Any]:
        """
        Extract features from a single packet.
        
        Args:
            packet: Scapy packet
            
        Returns:
            Dictionary of packet features
        """
        features = {}
        
        try:
            # Basic packet features
            features['length'] = len(packet)
            features['time'] = packet.time
            
            # IP layer features
            if packet.haslayer('IP'):
                ip = packet['IP']
                features['ip_len'] = ip.len
                features['ip_ttl'] = ip.ttl
                features['ip_proto'] = ip.proto
                features['ip_flags'] = ip.flags
                features['ip_tos'] = ip.tos
                
                # Convert IP addresses to integers for ML
                features['src_ip_int'] = int.from_bytes(
                    bytes(map(int, ip.src.split('.'))), byteorder='big'
                )
                features['dst_ip_int'] = int.from_bytes(
                    bytes(map(int, ip.dst.split('.'))), byteorder='big'
                )
                
                # Geographical features could be added here with IP geolocation
            
            # TCP layer features
            if packet.haslayer('TCP'):
                tcp = packet['TCP']
                features['src_port'] = tcp.sport
                features['dst_port'] = tcp.dport
                features['tcp_flags'] = tcp.flags
                features['tcp_window'] = tcp.window
                
                # Individual TCP flags
                features['tcp_syn'] = 1 if tcp.flags & 0x02 else 0
                features['tcp_ack'] = 1 if tcp.flags & 0x10 else 0
                features['tcp_fin'] = 1 if tcp.flags & 0x01 else 0
                features['tcp_rst'] = 1 if tcp.flags & 0x04 else 0
                features['tcp_psh'] = 1 if tcp.flags & 0x08 else 0
                features['tcp_urg'] = 1 if tcp.flags & 0x20 else 0
            
            # UDP layer features
            if packet.haslayer('UDP'):
                udp = packet['UDP']
                features['src_port'] = udp.sport
                features['dst_port'] = udp.dport
                features['udp_len'] = udp.len
            
            # ICMP layer features
            if packet.haslayer('ICMP'):
                icmp = packet['ICMP']
                features['icmp_type'] = icmp.type
                features['icmp_code'] = icmp.code
            
            # HTTP layer features
            if packet.haslayer(http.HTTPRequest):
                http_req = packet[http.HTTPRequest]
                features['is_http'] = 1
                features['http_method'] = http_req.Method.decode() if http_req.Method else ''
                features['http_path_len'] = len(http_req.Path) if http_req.Path else 0
                
            # TLS layer features
            if packet.haslayer(tls.TLS):
                features['is_tls'] = 1
                tls_layer = packet[tls.TLS]
                features['tls_type'] = tls_layer.type if hasattr(tls_layer, 'type') else 0
                
            # DNS layer features
            if packet.haslayer('DNS'):
                features['is_dns'] = 1
                dns = packet['DNS']
                features['dns_qd_count'] = dns.qdcount
                features['dns_an_count'] = dns.ancount
                
            logger.debug(f"Extracted {len(features)} features from packet")
            
        except Exception as e:
            logger.error(f"Error extracting features from packet: {str(e)}")
        
        return features
    
    def extract_pcap_features(self, pcap_file: str, max_packets: int = 1000) -> List[Dict[str, Any]]:
        """
        Extract features from a pcap file.
        
        Args:
            pcap_file: Path to the pcap file
            max_packets: Maximum number of packets to process
            
        Returns:
            List of packet feature dictionaries
        """
        features_list = []
        
        try:
            logger.info(f"Processing PCAP file: {pcap_file}")
            packets = scapy.rdpcap(pcap_file, count=max_packets)
            
            for packet in packets:
                features = self.extract_packet_features(packet)
                if features:
                    features_list.append(features)
            
            logger.info(f"Extracted features from {len(features_list)} packets in {pcap_file}")
            
        except Exception as e:
            logger.error(f"Error processing PCAP file: {str(e)}")
        
        return features_list
    
    def extract_behavioral_features(self, flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract behavioral features from a collection of flows.
        These features capture patterns across multiple flows.
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            Dictionary of behavioral features
        """
        features = {}
        
        try:
            if not flows:
                return features
            
            # Calculate unique IP addresses and ports
            src_ips = set()
            dst_ips = set()
            src_ports = set()
            dst_ports = set()
            protocols = set()
            
            # Statistics counters
            total_bytes = 0
            total_packets = 0
            start_times = []
            end_times = []
            
            # Connection counts by protocol
            tcp_flows = 0
            udp_flows = 0
            icmp_flows = 0
            
            # Flag counts across TCP flows
            syn_count = 0
            fin_count = 0
            rst_count = 0
            
            # Process all flows
            for flow in flows:
                # Count unique IPs and ports
                src_ips.add(flow.get('src_ip'))
                dst_ips.add(flow.get('dst_ip'))
                src_ports.add(flow.get('src_port'))
                dst_ports.add(flow.get('dst_port'))
                protocols.add(flow.get('protocol'))
                
                # Accumulate statistics
                total_bytes += flow.get('bytes', 0)
                total_packets += flow.get('packets', 0)
                
                if 'start_time' in flow:
                    start_times.append(flow['start_time'])
                if 'end_time' in flow:
                    end_times.append(flow['end_time'])
                
                # Count by protocol
                protocol = flow.get('protocol', '').lower()
                if protocol == 'tcp':
                    tcp_flows += 1
                elif protocol == 'udp':
                    udp_flows += 1
                elif protocol == 'icmp':
                    icmp_flows += 1
                
                # Accumulate flag counts
                if 'tcp_flags' in flow:
                    flags = flow['tcp_flags']
                    syn_count += flags.get('syn', 0)
                    fin_count += flags.get('fin', 0)
                    rst_count += flags.get('rst', 0)
            
            # Calculate behavioral features
            features['unique_src_ips'] = len(src_ips)
            features['unique_dst_ips'] = len(dst_ips)
            features['unique_src_ports'] = len(src_ports)
            features['unique_dst_ports'] = len(dst_ports)
            features['unique_protocols'] = len(protocols)
            
            features['total_flows'] = len(flows)
            features['total_bytes'] = total_bytes
            features['total_packets'] = total_packets
            
            features['tcp_flow_ratio'] = tcp_flows / len(flows) if flows else 0
            features['udp_flow_ratio'] = udp_flows / len(flows) if flows else 0
            features['icmp_flow_ratio'] = icmp_flows / len(flows) if flows else 0
            
            # Time-based features
            if start_times and end_times:
                min_start = min(start_times)
                max_end = max(end_times)
                duration_sec = (max_end - min_start) / 1000000  # μs to seconds
                
                if duration_sec > 0:
                    features['flows_per_second'] = len(flows) / duration_sec
                    features['bytes_per_second'] = total_bytes / duration_sec
                    features['packets_per_second'] = total_packets / duration_sec
            
            # Flag-based features
            if tcp_flows > 0:
                features['syn_per_flow'] = syn_count / tcp_flows
                features['fin_per_flow'] = fin_count / tcp_flows
                features['rst_per_flow'] = rst_count / tcp_flows
            
            # Scan detection features
            if len(src_ips) > 0:
                features['dst_ip_to_src_ip_ratio'] = len(dst_ips) / len(src_ips)
            if len(src_ports) > 0:
                features['dst_port_to_src_port_ratio'] = len(dst_ports) / len(src_ports)
                
            logger.debug(f"Extracted {len(features)} behavioral features from {len(flows)} flows")
            
        except Exception as e:
            logger.error(f"Error extracting behavioral features: {str(e)}")
        
        return features
    
    def normalize_features(self, features: Dict[str, Any], normalization_values: Dict[str, Dict[str, float]] = None) -> Dict[str, float]:
        """
        Normalize features using standard scaling (z-score normalization).
        
        Args:
            features: Dictionary of features to normalize
            normalization_values: Dictionary with mean and std for each feature
            
        Returns:
            Dictionary of normalized features
        """
        normalized = {}
        
        # If no normalization values provided, return original features
        if not normalization_values:
            return {k: float(v) for k, v in features.items() if isinstance(v, (int, float))}
        
        for key, value in features.items():
            if key in normalization_values and isinstance(value, (int, float)):
                mean = normalization_values[key].get('mean', 0)
                std = normalization_values[key].get('std', 1)
                
                # Avoid division by zero
                if std > 0:
                    normalized[key] = (value - mean) / std
                else:
                    normalized[key] = value - mean
            elif isinstance(value, (int, float)):
                # For features without normalization values, keep as is
                normalized[key] = float(value)
        
        return normalized