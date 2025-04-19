FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpcap-dev \
    tcpdump \
    tshark \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install packet capture-specific requirements
COPY packet_capture/requirements.txt packet_capture/requirements.txt
RUN pip install --no-cache-dir -r packet_capture/requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/pcap

# Copy source code
COPY packet_capture/ /app/packet_capture/

# Set environment variables
ENV PYTHONPATH=/app
ENV PCAP_DIR=/app/data/pcap
ENV LOG_LEVEL=INFO

# Need to run as root for packet capture permissions
# But drop capabilities as much as possible when running 
# Only NET_ADMIN and NET_RAW are needed

# Run the application
ENTRYPOINT ["python", "-m", "packet_capture.src.capture"]