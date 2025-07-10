# backend/processor.py

import time

class PacketProcessor:
    """
    Processes raw packets to extract a structured feature vector.
    """
    def __init__(self, analysis_callback=None):
        """
        Initializes the Packet Processor.
        
        Args:
            analysis_callback (callable): An awaitable callback function to send the 
                                          extracted feature vector to for further analysis 
                                          (e.g., ML detection, graph update).
        """
        self.analysis_callback = analysis_callback

    async def process_packet(self, packet):
        """
        Processes a single packet to extract key features. This method serves as the
        bridge between raw network data and a structured format for analysis.
        
        Args:
            packet (pyshark.packet.Packet): The raw packet object from PyShark.
        """
        try:
            # Core 5-tuple for flow identification. We check for the 'ip' layer first.
            if 'IP' not in packet:
                return # Ignore non-IP packets for this NIDS

            src_addr = packet.ip.src
            dst_addr = packet.ip.dst
            protocol = packet.transport_layer  # e.g., 'TCP', 'UDP'
            
            # Transport layer details might not always be present.
            if protocol:
                src_port = packet[protocol].srcport
                dst_port = packet[protocol].dstport
            else:
                src_port, dst_port = 0, 0 # Default for non-transport layer IP packets like ICMP

            # Packet-level features are fundamental for anomaly detection.
            packet_length = int(packet.length)
            timestamp = float(packet.sniff_timestamp)

            # Extracting TCP flags is crucial for identifying scan types and connection states.
            tcp_flags_hex = 0
            if 'TCP' in packet:
                # The 'flags' attribute is a hex string (e.g., '0x002' for SYN).
                tcp_flags_hex = int(packet.tcp.flags, 16)

            # Construct the feature vector. This is the standardized data structure
            # that will be used throughout the rest of the system.
            feature_vector = {
                'timestamp': timestamp,
                'src_addr': src_addr,
                'dst_addr': dst_addr,
                'protocol': protocol,
                'src_port': int(src_port),
                'dst_port': int(dst_port),
                'packet_length': packet_length,
                'tcp_flags': tcp_flags_hex,
            }

            # Pass the structured data to the next stage in the pipeline.
            if self.analysis_callback:
                await self.analysis_callback(feature_vector)

        except AttributeError:
            # This handles cases where a packet has an IP layer but is malformed
            # or lacks expected attributes. We can safely ignore these for the prototype.
            pass
