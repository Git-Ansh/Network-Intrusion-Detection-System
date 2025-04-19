FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ML-specific requirements
COPY ml_engine/requirements.txt ml_engine/requirements.txt
RUN pip install --no-cache-dir -r ml_engine/requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/models

# Copy source code
COPY ml_engine/ /app/ml_engine/

# Set environment variables
ENV PYTHONPATH=/app
ENV MODELS_DIR=/app/data/models
ENV LOG_LEVEL=INFO

# Create a non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run the application
ENTRYPOINT ["python", "-m", "ml_engine.src.app"]
CMD ["--mode", "inference"]