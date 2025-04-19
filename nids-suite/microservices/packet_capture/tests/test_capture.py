# Contents of /nids-suite/nids-suite/microservices/packet_capture/tests/test_capture.py

import unittest
from unittest.mock import patch, MagicMock
from src.capture import PacketCapture

class TestPacketCapture(unittest.TestCase):

    @patch('src.capture.pcapy')
    def test_start_capture(self, mock_pcapy):
        mock_capture = MagicMock()
        mock_pcapy.open_live.return_value = mock_capture
        
        packet_capture = PacketCapture(interface='eth0')
        packet_capture.start_capture()

        mock_pcapy.open_live.assert_called_once_with('eth0', 65536, 1, 0, 'capture')
        mock_capture.loop.assert_called_once_with(-1, packet_capture.packet_handler)

    def test_packet_handler(self):
        packet_capture = PacketCapture(interface='eth0')
        packet_data = b'\x00\x01\x02\x03'  # Example packet data

        with patch('src.capture.process_packet') as mock_process_packet:
            packet_capture.packet_handler(packet_data)

            mock_process_packet.assert_called_once_with(packet_data)

if __name__ == '__main__':
    unittest.main()