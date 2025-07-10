# backend/sniffer.py

import pyshark
import asyncio
import sys

class TrafficSniffer:
    """
    A class to capture network traffic in real-time using PyShark.
    """
    def __init__(self, interface='eth0', packet_callback=None):
        """
        Initializes the Traffic Sniffer.
        
        Args:
            interface (str): The network interface to sniff on (e.g., 'eth0', 'en0').
            packet_callback (callable): An awaitable callback function to be invoked 
                                        for each captured packet. It should accept one 
                                        argument: the packet object.
        """
        self.interface = interface
        self.packet_callback = packet_callback
        # Check for root privileges, which are necessary for packet sniffing.
        # Note: In Docker, this is handled by `cap_add`, but it's good practice for standalone use.
        # if os.geteuid() != 0:
        #     print("[!] Packet sniffing requires root privileges. Please run with sudo.")
        #     sys.exit(1)

    async def start_sniffing(self):
        """
        Starts sniffing network traffic on the specified interface asynchronously.
        It uses PyShark's LiveCapture for real-time packet capture and passes
        each packet to the registered callback for processing.
        """
        print(f"[*] Starting network capture on interface {self.interface}...")
        try:
            # pyshark.LiveCapture provides an async iterator over captured packets.
            capture = pyshark.LiveCapture(interface=self.interface)

            # The sniff_continuously method is ideal for long-running, non-terminating captures.
            async for packet in capture.sniff_continuously():
                if self.packet_callback:
                    # Schedule the callback to run without blocking the capture loop.
                    asyncio.create_task(self.packet_callback(packet))

        except asyncio.CancelledError:
            print("\n[*] Stopping network capture.")
        except Exception as e:
            # This can catch issues like the interface not existing.
            print(f"[!] An error occurred during sniffing on interface '{self.interface}': {e}", file=sys.stderr)
            print("[!] Please ensure the interface exists and you have the necessary permissions.", file=sys.stderr)
        finally:
            if 'capture' in locals() and capture.eventloop.is_running():
                capture.close()
