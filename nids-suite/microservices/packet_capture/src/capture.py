#!/usr/bin/env python3
"""
Network packet capture module using Scapy.
This module provides functionality to capture, analyze, and forward network packets.
"""

import os
import sys
import time
import signal
import logging
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from queue import Queue, Empty
from datetime import datetime
import argparse

import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.packet import Packet

# Local imports
from flow_builder import FlowBuilder, Flow
from feature_extraction import FeatureExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO if not os.getenv('LOG_LEVEL') else os.getenv('LOG_LEVEL'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default values
DEFAULT_INTERFACE = None  # Auto-select
DEFAULT_BPF_FILTER = "ip"  # Capture only IP traffic
DEFAULT_SNAPLEN = 65535  # Maximum packet capture length
DEFAULT_BATCH_SIZE = 1000  # Number of packets to process in a batch
DEFAULT_EXPORT_INTERVAL = 10  # Seconds between flow exports

class PacketCapture:
    """
    Network packet capture using Scapy with flow tracking and feature extraction.
    """
    
    def __init__(
        self,
        interface: Optional[str] = DEFAULT_INTERFACE,
        bpf_filter: str = DEFAULT_BPF_FILTER,
        snaplen: int = DEFAULT_SNAPLEN,
        promisc: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
        export_interval: int = DEFAULT_EXPORT_INTERVAL,
        output_file: Optional[str] = None,
        kafka_output: bool = False,
        kafka_topic: Optional[str] = None,
        kafka_server: Optional[str] = None,
    ):
        """
        Initialize packet capture.
        
        Args:
            interface: Network interface to sniff on (None for auto)
            bpf_filter: BPF filter string
            snaplen: Maximum number of bytes to capture per packet
            promisc: Whether to enable promiscuous mode
            batch_size: Number of packets to process in a batch
            export_interval: Seconds between flow exports
            output_file: Optional file to write flow data to (JSON format)
            kafka_output: Whether to send flow data to Kafka
            kafka_topic: Kafka topic to send flow data to
            kafka_server: Kafka server address (host:port)
        """
        self.interface = interface
        self.bpf_filter = bpf_filter
        self.snaplen = snaplen
        self.promisc = promisc
        self.batch_size = batch_size
        self.export_interval = export_interval
        self.output_file = output_file
        self.kafka_output = kafka_output
        self.kafka_topic = kafka_topic
        self.kafka_server = kafka_server
        
        # Initialize components
        self.flow_builder = FlowBuilder(bidirectional=True)
        self.feature_extractor = FeatureExtractor()
        
        # Initialize state
        self.packet_queue = Queue(maxsize=100000)  # Buffer for up to 100K packets
        self.running = False
        self.stats = {
            "start_time": None,
            "end_time": None,
            "packets_captured": 0,
            "packets_processed": 0,
            "bytes_captured": 0,
            "flows_created": 0,
            "flows_exported": 0,
        }
        
        # Initialize threads
        self.sniffer_thread = None
        self.processor_thread = None
        self.exporter_thread = None
        
        # Kafka producer (lazy initialized if needed)
        self.kafka_producer = None
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Packet capture initialized (interface={interface or 'auto'}, "
                    f"filter='{bpf_filter}', snaplen={snaplen})")
    
    def _init_kafka(self) -> None:
        """Initialize Kafka producer if needed"""
        if not self.kafka_output or self.kafka_producer is not None:
            return
        
        try:
            from kafka import KafkaProducer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.kafka_server,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                compression_type='gzip'
            )
            logger.info(f"Kafka producer initialized (server={self.kafka_server}, "
                        f"topic={self.kafka_topic})")
        except ImportError:
            logger.error("Kafka output requested but kafka-python package is not installed")
            self.kafka_output = False
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.kafka_output = False
    
    def _packet_callback(self, packet: Packet) -> None:
        """
        Callback function for packet processing.
        
        Args:
            packet: Scapy packet
        """
        try:
            # Increment counters
            self.stats["packets_captured"] += 1
            self.stats["bytes_captured"] += len(packet)
            
            # Add packet to queue for processing
            if not self.packet_queue.full():
                self.packet_queue.put(packet)
            else:
                logger.warning("Packet queue full, dropping packet")
        except Exception as e:
            logger.error(f"Error in packet callback: {e}")
    
    def _process_packet_batch(self) -> None:
        """Process a batch of packets from the queue"""
        batch = []
        start_time = time.time()
        
        # Get up to batch_size packets from queue
        while len(batch) < self.batch_size:
            try:
                # Non-blocking queue get with timeout
                packet = self.packet_queue.get(block=True, timeout=0.1)
                batch.append(packet)
                self.packet_queue.task_done()
            except Empty:
                # No more packets in queue
                break
        
        # Process the batch
        if batch:
            for packet in batch:
                # Process packet through flow builder
                flow = self.flow_builder.process_packet(packet)
                if flow is not None and flow.is_expired:
                    # Flow just expired, extract features and export
                    features = self.feature_extractor.extract_flow_features(flow)
                    self._export_flow(flow, features)
            
            # Update stats
            self.stats["packets_processed"] += len(batch)
            
            # Log processing rate
            elapsed = time.time() - start_time
            if elapsed > 0:
                rate = len(batch) / elapsed
                logger.debug(f"Processed {len(batch)} packets in {elapsed:.3f}s ({rate:.1f} pps)")
    
    def _export_flows_periodically(self) -> None:
        """Export flows periodically"""
        while self.running:
            # Sleep for export interval
            time.sleep(self.export_interval)
            
            # Get expired flows
            flows = self.flow_builder.get_expired_flows()
            
            # Process and export each flow
            for flow in flows:
                features = self.feature_extractor.extract_flow_features(flow)
                self._export_flow(flow, features)
            
            # Log statistics
            if flows:
                logger.info(f"Exported {len(flows)} flows")
                self.stats["flows_exported"] += len(flows)
    
    def _export_flow(self, flow: Flow, features: Dict[str, Any]) -> None:
        """
        Export a flow with extracted features.
        
        Args:
            flow: Flow object
            features: Extracted features dictionary
        """
        # Combine flow data with features
        export_data = {
            "flow": flow.to_dict(),
            "features": features,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Write to file if configured
        if self.output_file:
            try:
                with open(self.output_file, 'a') as f:
                    f.write(json.dumps(export_data) + '\n')
            except Exception as e:
                logger.error(f"Error writing to output file: {e}")
        
        # Send to Kafka if configured
        if self.kafka_output and self.kafka_producer:
            try:
                self.kafka_producer.send(self.kafka_topic, export_data)
            except Exception as e:
                logger.error(f"Error sending to Kafka: {e}")
    
    def _processor_loop(self) -> None:
        """Main packet processing loop"""
        logger.info("Packet processor started")
        
        while self.running:
            try:
                self._process_packet_batch()
            except Exception as e:
                logger.error(f"Error in processor loop: {e}")
    
    def _signal_handler(self, sig, frame) -> None:
        """Handle signals for graceful shutdown"""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
    
    def start(self) -> None:
        """Start packet capture and processing"""
        if self.running:
            logger.warning("Packet capture already running")
            return
        
        self.running = True
        self.stats["start_time"] = time.time()
        
        # Initialize Kafka if needed
        if self.kafka_output:
            self._init_kafka()
        
        # Start processor thread
        self.processor_thread = threading.Thread(
            target=self._processor_loop,
            daemon=True
        )
        self.processor_thread.start()
        
        # Start exporter thread
        self.exporter_thread = threading.Thread(
            target=self._export_flows_periodically,
            daemon=True
        )
        self.exporter_thread.start()
        
        # Start packet sniffer
        logger.info(f"Starting packet capture on interface {self.interface or 'auto'}")
        
        try:
            self.sniffer_thread = threading.Thread(
                target=lambda: scapy.sniff(
                    iface=self.interface,
                    filter=self.bpf_filter,
                    prn=self._packet_callback,
                    store=False,
                    snaplen=self.snaplen
                ),
                daemon=True
            )
            self.sniffer_thread.start()
        except Exception as e:
            logger.error(f"Error starting sniffer: {e}")
            self.running = False
            raise
    
    def stop(self) -> None:
        """Stop packet capture and processing"""
        if not self.running:
            return
        
        logger.info("Stopping packet capture...")
        self.running = False
        self.stats["end_time"] = time.time()
        
        # Wait for processor to finish
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5.0)
        
        # Wait for exporter to finish
        if self.exporter_thread and self.exporter_thread.is_alive():
            self.exporter_thread.join(timeout=5.0)
        
        # Process any remaining packets in queue
        while not self.packet_queue.empty():
            self._process_packet_batch()
        
        # Export any remaining flows
        remaining_flows = self.flow_builder.expire_all_flows()
        for flow in remaining_flows:
            features = self.feature_extractor.extract_flow_features(flow)
            self._export_flow(flow, features)
        
        # Flush Kafka producer if used
        if self.kafka_producer:
            self.kafka_producer.flush()
        
        # Log final stats
        duration = self.stats["end_time"] - self.stats["start_time"]
        pps = self.stats["packets_processed"] / duration if duration > 0 else 0
        logger.info(f"Packet capture finished: "
                    f"{self.stats['packets_processed']} packets processed "
                    f"({pps:.1f} pps), "
                    f"{self.stats['flows_exported']} flows exported")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get capture statistics.
        
        Returns:
            Dictionary of statistics
        """
        # Update stats from components
        self.stats["flow_builder"] = self.flow_builder.get_stats()
        
        # Calculate derived stats
        if self.stats["start_time"] is not None:
            current_time = time.time() if not self.stats["end_time"] else self.stats["end_time"]
            duration = current_time - self.stats["start_time"]
            
            if duration > 0:
                self.stats["packets_per_second"] = self.stats["packets_processed"] / duration
                self.stats["bytes_per_second"] = self.stats["bytes_captured"] / duration
        
        return self.stats
    
    def is_running(self) -> bool:
        """Check if capture is running"""
        return self.running

def main():
    """Command line entry point"""
    parser = argparse.ArgumentParser(
        description='Network packet capture with flow tracking and feature extraction'
    )
    parser.add_argument('-i', '--interface', help='Network interface to capture from')
    parser.add_argument('-f', '--filter', default=DEFAULT_BPF_FILTER,
                       help='BPF filter expression')
    parser.add_argument('-s', '--snaplen', type=int, default=DEFAULT_SNAPLEN,
                       help='Snapshot length (max bytes per packet)')
    parser.add_argument('-p', '--promiscuous', action='store_true',
                       help='Enable promiscuous mode')
    parser.add_argument('-b', '--batch-size', type=int, default=DEFAULT_BATCH_SIZE,
                       help='Batch size for packet processing')
    parser.add_argument('-e', '--export-interval', type=int, default=DEFAULT_EXPORT_INTERVAL,
                       help='Flow export interval in seconds')
    parser.add_argument('-o', '--output', help='Output file for flow data (JSON lines)')
    parser.add_argument('-k', '--kafka', action='store_true',
                       help='Enable Kafka output')
    parser.add_argument('-t', '--kafka-topic', default='nids-flows',
                       help='Kafka topic for flow data')
    parser.add_argument('-s', '--kafka-server', default='localhost:9092',
                       help='Kafka server (host:port)')
    parser.add_argument('-d', '--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start packet capture
    capture = PacketCapture(
        interface=args.interface,
        bpf_filter=args.filter,
        snaplen=args.snaplen,
        promisc=args.promiscuous,
        batch_size=args.batch_size,
        export_interval=args.export_interval,
        output_file=args.output,
        kafka_output=args.kafka,
        kafka_topic=args.kafka_topic,
        kafka_server=args.kafka_server,
    )
    
    try:
        capture.start()
        
        # Keep main thread alive
        while capture.is_running():
            time.sleep(1.0)
            
            # Print stats every 10 seconds
            if int(time.time()) % 10 == 0:
                stats = capture.get_stats()
                pps = stats.get("packets_per_second", 0)
                active_flows = stats.get("flow_builder", {}).get("active_flows", 0)
                
                print(f"Packets: {stats['packets_processed']}, "
                      f"Rate: {pps:.1f} pps, "
                      f"Active flows: {active_flows}")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        capture.stop()

if __name__ == "__main__":
    main()