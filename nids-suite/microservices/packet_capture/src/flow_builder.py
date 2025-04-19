#!/usr/bin/env python3
"""
Flow builder module for the packet capture service.
Constructs network flows from individual packets for analysis.
"""

import os
import time
import logging
import uuid
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from scapy.packet import Packet
from scapy.layers.inet import IP, TCP, UDP, ICMP

# Configure logging
logging.basicConfig(
    level=logging.INFO if not os.getenv('LOG_LEVEL') else os.getenv('LOG_LEVEL'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flow timeout values in seconds
ACTIVE_TIMEOUT = 300  # 5 minutes
INACTIVE_TIMEOUT = 60  # 1 minute

class FlowKey:
    """
    Flow key class to identify network flows.
    A flow is defined by a 5-tuple: src_ip, dst_ip, src_port, dst_port, protocol
    """
    
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str):
        """
        Initialize a flow key.
        
        Args:
            src_ip: Source IP address
            dst_ip: Destination IP address
            src_port: Source port (0 for ICMP)
            dst_port: Destination port (0 for ICMP)
            protocol: Protocol (TCP, UDP, ICMP, etc.)
        """
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port if src_port is not None else 0
        self.dst_port = dst_port if dst_port is not None else 0
        self.protocol = protocol
        
    def __eq__(self, other):
        """Check if two flow keys are equal"""
        if not isinstance(other, FlowKey):
            return False
        return (
            self.src_ip == other.src_ip and
            self.dst_ip == other.dst_ip and
            self.src_port == other.src_port and
            self.dst_port == other.dst_port and
            self.protocol == other.protocol
        )
    
    def __hash__(self):
        """Hash function for use in dictionaries"""
        return hash((self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol))
    
    def reversed(self) -> 'FlowKey':
        """
        Get a reversed version of this flow key (for bidirectional flows).
        
        Returns:
            A new FlowKey with source and destination properties swapped
        """
        return FlowKey(
            src_ip=self.dst_ip,
            dst_ip=self.src_ip,
            src_port=self.dst_port,
            dst_port=self.src_port,
            protocol=self.protocol
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the flow key to a dictionary.
        
        Returns:
            Dictionary representation of the flow key
        """
        return {
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'protocol': self.protocol
        }
    
    def __str__(self) -> str:
        """String representation of the flow key"""
        return f"{self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port} ({self.protocol})"

class Flow:
    """
    Flow class to track network connections over time.
    """
    
    def __init__(self, key: FlowKey, bidirectional: bool = True):
        """
        Initialize a new flow.
        
        Args:
            key: The flow key
            bidirectional: Whether to track both directions of the flow
        """
        self.key = key
        self.id = str(uuid.uuid4())
        self.bidirectional = bidirectional
        
        # Flow statistics
        self.start_time = None
        self.last_time = None
        self.end_time = None
        self.bytes = 0
        self.packets = 0
        self.packet_times: List[float] = []
        self.packet_sizes: List[int] = []
        self.inter_arrival_times: List[float] = []
        
        # TCP specific
        self.tcp_flags: Dict[str, int] = {
            'fin': 0, 'syn': 0, 'rst': 0, 'psh': 0,
            'ack': 0, 'urg': 0, 'ece': 0, 'cwr': 0
        }
        
        # Flow state
        self.state = 'new'  # new, established, closing, closed, reset
        self.is_expired = False
        
        logger.debug(f"Created new flow: {self.key}")
    
    def add_packet(self, packet: Packet, timestamp: Optional[float] = None) -> None:
        """
        Add a packet to this flow.
        
        Args:
            packet: Scapy packet
            timestamp: Optional timestamp (if None, use packet.time)
        """
        if not packet.haslayer('IP'):
            return
        
        # Get basic packet info
        ip_layer = packet.getlayer('IP')
        size = len(packet)
        pkt_time = timestamp if timestamp is not None else packet.time
        
        # Update flow timestamps
        if self.start_time is None:
            self.start_time = pkt_time
        
        # Calculate inter-arrival time
        if self.last_time is not None:
            iat = pkt_time - self.last_time
            self.inter_arrival_times.append(iat)
        
        # Update last seen time
        self.last_time = pkt_time
        
        # Update packet statistics
        self.packets += 1
        self.bytes += size
        self.packet_times.append(pkt_time)
        self.packet_sizes.append(size)
        
        # Process TCP flags
        if packet.haslayer('TCP'):
            tcp = packet.getlayer('TCP')
            flags = tcp.flags
            
            # Update TCP flag counts
            if flags & 0x01:  # FIN
                self.tcp_flags['fin'] += 1
            if flags & 0x02:  # SYN
                self.tcp_flags['syn'] += 1
            if flags & 0x04:  # RST
                self.tcp_flags['rst'] += 1
            if flags & 0x08:  # PSH
                self.tcp_flags['psh'] += 1
            if flags & 0x10:  # ACK
                self.tcp_flags['ack'] += 1
            if flags & 0x20:  # URG
                self.tcp_flags['urg'] += 1
            if flags & 0x40:  # ECE
                self.tcp_flags['ece'] += 1
            if flags & 0x80:  # CWR
                self.tcp_flags['cwr'] += 1
            
            # Update flow state based on flags
            self._update_tcp_state(flags)
        
        logger.debug(f"Added packet to flow {self.id}, now has {self.packets} packets, {self.bytes} bytes")
    
    def _update_tcp_state(self, flags: int) -> None:
        """
        Update the TCP state based on observed flags.
        
        Args:
            flags: TCP flags from the current packet
        """
        # Simple state machine for TCP connection tracking
        if self.state == 'new':
            if flags & 0x02:  # SYN
                self.state = 'syn_sent'
            elif flags & 0x12:  # SYN-ACK
                self.state = 'syn_received'
        
        elif self.state in ('syn_sent', 'syn_received'):
            if flags & 0x10:  # ACK
                self.state = 'established'
        
        elif self.state == 'established':
            if flags & 0x01:  # FIN
                self.state = 'closing'
            elif flags & 0x04:  # RST
                self.state = 'reset'
        
        elif self.state == 'closing':
            if flags & 0x01:  # FIN (from other side)
                self.state = 'close_wait'
            elif flags & 0x04:  # RST
                self.state = 'reset'
        
        elif self.state == 'close_wait':
            if flags & 0x10:  # ACK
                self.state = 'closed'
    
    def is_tcp_established(self) -> bool:
        """Check if the TCP connection was fully established"""
        return self.state in ('established', 'closing', 'close_wait', 'closed')
    
    def is_inactive(self, current_time: float, timeout: float = INACTIVE_TIMEOUT) -> bool:
        """
        Check if the flow is inactive (no packets for timeout period).
        
        Args:
            current_time: Current timestamp
            timeout: Timeout in seconds
            
        Returns:
            True if inactive, False otherwise
        """
        if self.last_time is None:
            return False
        
        return (current_time - self.last_time) > timeout
    
    def is_active_timeout(self, current_time: float, timeout: float = ACTIVE_TIMEOUT) -> bool:
        """
        Check if the flow has been active for too long.
        
        Args:
            current_time: Current timestamp
            timeout: Timeout in seconds
            
        Returns:
            True if flow has been active too long, False otherwise
        """
        if self.start_time is None:
            return False
        
        return (current_time - self.start_time) > timeout
    
    def expire(self, timestamp: Optional[float] = None) -> None:
        """
        Mark this flow as expired.
        
        Args:
            timestamp: Optional timestamp to use as end time
        """
        if timestamp is not None:
            self.end_time = timestamp
        elif self.last_time is not None:
            self.end_time = self.last_time
        else:
            self.end_time = time.time()
        
        self.is_expired = True
        logger.debug(f"Flow {self.id} marked as expired")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the flow to a dictionary.
        
        Returns:
            Dictionary representation of the flow
        """
        # Convert from seconds to microseconds for consistency
        start_time_us = int(self.start_time * 1000000) if self.start_time else None
        end_time_us = int(self.end_time * 1000000) if self.end_time else None
        
        result = {
            'flow_id': self.id,
            'bidirectional': self.bidirectional,
            'start_time': start_time_us,
            'end_time': end_time_us,
            'bytes': self.bytes,
            'packets': self.packets,
            'state': self.state,
            'tcp_flags': self.tcp_flags.copy(),
        }
        
        # Add flow key information
        result.update(self.key.to_dict())
        
        # Add packet timing statistics if available
        if self.packet_sizes:
            result['packet_sizes'] = self.packet_sizes.copy()
        
        if self.inter_arrival_times:
            result['inter_arrival_times'] = self.inter_arrival_times.copy()
        
        # Calculate duration (microseconds)
        if start_time_us is not None and end_time_us is not None:
            result['duration_us'] = end_time_us - start_time_us
        
        return result

class FlowBuilder:
    """
    Builds network flows from packets.
    
    This class processes packets to construct flow records that can be used
    for network traffic analysis and intrusion detection.
    """
    
    def __init__(
        self,
        bidirectional: bool = True,
        active_timeout: int = ACTIVE_TIMEOUT,
        inactive_timeout: int = INACTIVE_TIMEOUT
    ):
        """
        Initialize the flow builder.
        
        Args:
            bidirectional: Whether to track bidirectional flows
            active_timeout: Maximum flow duration in seconds
            inactive_timeout: Flow inactivity timeout in seconds
        """
        self.flows: Dict[FlowKey, Flow] = {}
        self.bidirectional = bidirectional
        self.active_timeout = active_timeout
        self.inactive_timeout = inactive_timeout
        
        self.expired_flows: List[Flow] = []
        self.last_expiry_check = time.time()
        
        # Performance metrics
        self.packets_processed = 0
        self.flows_created = 0
        self.flows_expired = 0
        
        logger.info(f"Flow builder initialized (bidirectional={bidirectional}, "
                    f"active_timeout={active_timeout}s, inactive_timeout={inactive_timeout}s)")
    
    def process_packet(self, packet: Packet) -> Optional[Flow]:
        """
        Process a packet and update corresponding flow.
        
        Args:
            packet: Scapy packet
            
        Returns:
            Flow object if the packet caused a flow to expire, None otherwise
        """
        # Check if this is an IP packet
        if not packet.haslayer('IP'):
            return None
        
        # Extract IP header
        ip = packet.getlayer('IP')
        src_ip = ip.src
        dst_ip = ip.dst
        protocol = None
        src_port = None
        dst_port = None
        
        # Extract transport layer info
        if packet.haslayer('TCP'):
            protocol = 'TCP'
            tcp = packet.getlayer('TCP')
            src_port = tcp.sport
            dst_port = tcp.dport
        elif packet.haslayer('UDP'):
            protocol = 'UDP'
            udp = packet.getlayer('UDP')
            src_port = udp.sport
            dst_port = udp.dport
        elif packet.haslayer('ICMP'):
            protocol = 'ICMP'
            # ICMP doesn't have ports, use 0
            src_port = 0
            dst_port = 0
        else:
            # Unknown protocol
            protocol = str(ip.proto)
            src_port = 0
            dst_port = 0
        
        # Create flow key
        flow_key = FlowKey(src_ip, dst_ip, src_port, dst_port, protocol)
        reversed_key = flow_key.reversed()
        
        # Update packet counter
        self.packets_processed += 1
        
        # Get timestamp
        timestamp = packet.time
        
        # Check if flow already exists
        if flow_key in self.flows:
            # Add packet to existing flow
            flow = self.flows[flow_key]
            flow.add_packet(packet, timestamp)
            
        elif self.bidirectional and reversed_key in self.flows:
            # Add packet to existing bidirectional flow
            flow = self.flows[reversed_key]
            flow.add_packet(packet, timestamp)
            
        else:
            # Create new flow
            flow = Flow(key=flow_key, bidirectional=self.bidirectional)
            flow.add_packet(packet, timestamp)
            self.flows[flow_key] = flow
            self.flows_created += 1
        
        # Periodically check for expired flows
        current_time = time.time()
        if current_time - self.last_expiry_check > 1:  # Check once per second
            self._expire_flows(current_time)
            self.last_expiry_check = current_time
        
        # For TCP RST or FIN-ACK, check if flow is complete
        if protocol == 'TCP':
            tcp = packet.getlayer('TCP')
            if tcp.flags & 0x04:  # RST flag
                if flow_key in self.flows:
                    expired_flow = self.flows.pop(flow_key)
                    expired_flow.expire(timestamp)
                    self.expired_flows.append(expired_flow)
                    self.flows_expired += 1
                    return expired_flow
            elif tcp.flags & 0x11 == 0x11:  # FIN+ACK flags
                if flow.state == 'closed':
                    # Connection is fully closed
                    if flow_key in self.flows:
                        expired_flow = self.flows.pop(flow_key)
                        expired_flow.expire(timestamp)
                        self.expired_flows.append(expired_flow)
                        self.flows_expired += 1
                        return expired_flow
        
        return None
    
    def _expire_flows(self, current_time: float) -> List[Flow]:
        """
        Expire flows based on timeouts.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            List of expired flows
        """
        keys_to_remove = []
        expired = []
        
        # Find flows that need to be expired
        for key, flow in self.flows.items():
            if (flow.is_active_timeout(current_time, self.active_timeout) or
                flow.is_inactive(current_time, self.inactive_timeout)):
                keys_to_remove.append(key)
                flow.expire(current_time)
                expired.append(flow)
        
        # Remove expired flows from active flows dict
        for key in keys_to_remove:
            if key in self.flows:
                self.flows.pop(key)
        
        # Add to expired flows list
        self.expired_flows.extend(expired)
        self.flows_expired += len(expired)
        
        if expired:
            logger.debug(f"Expired {len(expired)} flows, {len(self.flows)} active flows remain")
        
        return expired
    
    def get_expired_flows(self) -> List[Flow]:
        """
        Get and clear the list of expired flows.
        
        Returns:
            List of expired flows
        """
        expired = self.expired_flows.copy()
        self.expired_flows.clear()
        return expired
    
    def get_active_flows(self) -> List[Flow]:
        """
        Get a list of all active flows.
        
        Returns:
            List of active flows
        """
        return list(self.flows.values())
    
    def expire_all_flows(self) -> List[Flow]:
        """
        Expire all active flows.
        
        Returns:
            List of all flows that were active
        """
        current_time = time.time()
        all_flows = list(self.flows.values())
        
        for flow in all_flows:
            flow.expire(current_time)
            self.expired_flows.append(flow)
        
        self.flows.clear()
        return all_flows
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get flow builder statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'packets_processed': self.packets_processed,
            'flows_created': self.flows_created,
            'flows_expired': self.flows_expired,
            'active_flows': len(self.flows),
            'expired_flows_buffered': len(self.expired_flows)
        }