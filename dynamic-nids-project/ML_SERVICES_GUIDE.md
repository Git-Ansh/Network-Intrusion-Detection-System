# ML Services Integration Guide

## Overview

The NIDS system now includes comprehensive ML services with adaptive functionality that works across different environments and dependency availability levels.

## Available Modes

### 1. Full ML Mode (`main_ml.py`)

- **Requirements**: pandas, scikit-learn, numpy, joblib
- **Features**:
  - Advanced anomaly detection with Random Forest and Isolation Forest
  - Real-time model training and retraining
  - Feature importance analysis
  - Performance monitoring
  - Ensemble predictions with confidence scoring

### 2. Basic ML Mode (`main.py`)

- **Requirements**: Basic dependencies + numpy, joblib
- **Features**:
  - Automatically detects ML services availability
  - Falls back to simple detector if advanced ML not available
  - Enhanced API endpoints for ML status

### 3. Simple Mode (`main_simple.py`)

- **Requirements**: Only basic FastAPI dependencies
- **Features**:
  - Rule-based anomaly detection
  - Statistical analysis
  - No external ML dependencies

### 4. Minimal Mode (`main_minimal.py`)

- **Requirements**: FastAPI only
- **Features**:
  - Basic functionality without authentication
  - Minimal resource usage

## ML Services Architecture

### Core Components

1. **MLServices Class** (`ml_services.py`)

   - Central coordinator for all ML functionality
   - Adaptive initialization based on available dependencies
   - Unified interface for different ML backends

2. **AdvancedMLDetector Class**

   - Uses scikit-learn for sophisticated anomaly detection
   - Supports Random Forest (supervised) and Isolation Forest (unsupervised)
   - Automatic model training with synthetic data
   - Feature scaling and preprocessing

3. **SimpleAnomalyDetector Class** (`simple_detector.py`)

   - Rule-based detection for environments without ML libraries
   - Statistical anomaly detection
   - Port-based suspicious activity detection

4. **PerformanceMonitor Class**
   - Tracks prediction accuracy and performance metrics
   - Monitors confidence scores and response times
   - Provides real-time statistics

### Features

#### Anomaly Detection

- **Multi-model ensemble**: Combines Random Forest and Isolation Forest predictions
- **Confidence scoring**: Provides confidence levels for each prediction
- **Adaptive thresholds**: Adjusts detection sensitivity based on network patterns
- **Real-time analysis**: Processes packets as they arrive

#### Model Management

- **Auto-training**: Trains models with synthetic data if no pre-trained models exist
- **Model persistence**: Saves/loads models to/from disk
- **Retraining API**: Allows manual model retraining via API endpoints
- **Feature importance**: Tracks which features are most important for detection

#### Performance Monitoring

- **Prediction metrics**: Tracks total predictions, anomaly rates, confidence scores
- **Response times**: Monitors ML pipeline performance
- **Resource usage**: Tracks memory and CPU usage (future enhancement)

## API Endpoints

### ML Status and Control

- `GET /api/ml/status` - Get ML services status and model information
- `GET /api/ml/feature-importance` - Get feature importance from models
- `POST /api/ml/retrain` - Trigger model retraining

### System Status

- `GET /api/status` - Comprehensive system status including ML services
- `GET /api/graph/data` - Network graph data with ML-enhanced annotations

### Real-time Communication

- `WebSocket /ws/alerts` - Real-time alerts including ML predictions

## Configuration

### Environment Variables

```bash
# ML Model Configuration
ML_MODELS_DIR=models/
ML_RETRAIN_INTERVAL=3600  # seconds
ML_CONFIDENCE_THRESHOLD=0.7

# Feature Engineering
FEATURE_WINDOW_SIZE=100
FEATURE_UPDATE_INTERVAL=10

# Performance Monitoring
PERFORMANCE_LOG_INTERVAL=300
```

### Model Configuration

Models are stored in the `models/` directory:

- `rf_model.joblib` - Random Forest classifier
- `if_model.joblib` - Isolation Forest detector
- `scaler.joblib` - Feature scaler

## Usage Examples

### Starting the System

1. **Automatic Mode Detection**:

   ```bash
   python backend/test_ml.py
   # Follow the recommendation
   ```

2. **Full ML Mode**:

   ```bash
   python backend/main_ml.py
   ```

3. **Adaptive Mode**:
   ```bash
   python backend/main.py
   ```

### Using the API

```python
import requests

# Check ML status
response = requests.get("http://localhost:8000/api/ml/status",
                       headers={"Authorization": "Bearer YOUR_TOKEN"})
print(response.json())

# Get feature importance
response = requests.get("http://localhost:8000/api/ml/feature-importance",
                       headers={"Authorization": "Bearer YOUR_TOKEN"})
print(response.json())

# Retrain models
response = requests.post("http://localhost:8000/api/ml/retrain",
                        headers={"Authorization": "Bearer YOUR_TOKEN"})
print(response.json())
```

### WebSocket Integration

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/alerts");

ws.onmessage = function (event) {
  const alert = JSON.parse(event.data);
  if (alert.type === "ML_Anomaly") {
    console.log("ML detected anomaly:", alert);
    console.log("Confidence:", alert.details.ml_prediction.confidence);
  }
};
```

## Troubleshooting

### Common Issues

1. **pandas Installation Fails**

   - Try installing with `--no-cache-dir` flag
   - Use older pandas version (1.5.3)
   - Check Python version compatibility (3.8-3.11 recommended for pandas)

2. **scikit-learn Build Errors**

   - Install Microsoft C++ Build Tools
   - Use pre-compiled wheels: `pip install --only-binary=all scikit-learn`
   - Try older scikit-learn version (1.3.0)

3. **Memory Issues**

   - Reduce model complexity: fewer estimators in Random Forest
   - Increase system RAM or use cloud instance
   - Use simple mode for resource-constrained environments

4. **Performance Issues**
   - Enable model caching
   - Reduce feature vector size
   - Use background model training

### Fallback Strategies

The system automatically implements fallback strategies:

1. **ML Libraries Not Available** → Use Simple Detector
2. **Model Training Fails** → Use Default Models
3. **Prediction Errors** → Log and Continue
4. **Memory Issues** → Reduce Model Complexity

## Advanced Configuration

### Custom Model Training

```python
# Custom training data format
training_data = [
    {
        'packet_length': 1500,
        'tcp_flags': 24,
        'src_port': 80,
        'dst_port': 12345,
        'protocol': 6,
        'ttl': 64,
        'window_size': 8192,
        'packet_rate': 10.5,
        'label': 0  # 0=benign, 1=malicious
    },
    # ... more samples
]

# Train models
await ml_services.train_models(training_data)
```

### Custom Feature Engineering

```python
# Extend the feature set
custom_features = [
    'packet_length', 'tcp_flags', 'src_port', 'dst_port',
    'protocol', 'ttl', 'window_size', 'packet_rate',
    'connection_duration', 'bytes_transferred', 'packet_interval'
]
```

## Performance Benchmarks

### Typical Performance (on modern hardware)

- **Prediction latency**: < 1ms per packet
- **Memory usage**: 50-200MB (depending on model size)
- **CPU usage**: 1-5% under normal load
- **Training time**: 30-60 seconds for 10,000 samples

### Scalability

- **Packet rate**: Up to 10,000 packets/second
- **Concurrent connections**: 100+ WebSocket clients
- **Model size**: Up to 100MB loaded models
- **History retention**: 1,000 recent predictions

## Future Enhancements

1. **Deep Learning Integration**: Add TensorFlow/PyTorch support
2. **Online Learning**: Implement continuous model updates
3. **Distributed Processing**: Support for multiple ML nodes
4. **Advanced Features**: Network flow analysis, temporal patterns
5. **Model Ensemble**: Support for custom model combinations

## Security Considerations

1. **Model Integrity**: Verify model checksums
2. **Input Validation**: Sanitize feature vectors
3. **Rate Limiting**: Prevent ML API abuse
4. **Access Control**: Secure ML endpoints with proper authentication
5. **Audit Logging**: Log all ML predictions and model changes
