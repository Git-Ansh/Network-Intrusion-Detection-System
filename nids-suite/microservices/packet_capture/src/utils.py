def get_packet_capture_data(packet):
    """
    Extract relevant data from a captured packet.

    Args:
        packet: The raw packet data.

    Returns:
        A dictionary containing extracted fields such as source IP, destination IP, 
        source port, destination port, and protocol.
    """
    # Placeholder for packet extraction logic
    extracted_data = {
        'src_ip': packet['ip']['src'],
        'dst_ip': packet['ip']['dst'],
        'src_port': packet['tcp']['srcport'],
        'dst_port': packet['tcp']['dstport'],
        'protocol': packet['transport_layer']
    }
    return extracted_data


def calculate_packet_statistics(packets):
    """
    Calculate statistics from a list of packets.

    Args:
        packets: A list of packet data.

    Returns:
        A dictionary containing statistics such as total packets, 
        average packet size, and protocol distribution.
    """
    total_packets = len(packets)
    total_size = sum(len(packet) for packet in packets)
    avg_size = total_size / total_packets if total_packets > 0 else 0

    protocol_distribution = {}
    for packet in packets:
        protocol = packet['transport_layer']
        if protocol not in protocol_distribution:
            protocol_distribution[protocol] = 0
        protocol_distribution[protocol] += 1

    return {
        'total_packets': total_packets,
        'average_packet_size': avg_size,
        'protocol_distribution': protocol_distribution
    }