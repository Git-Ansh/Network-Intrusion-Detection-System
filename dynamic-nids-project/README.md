# Dynamic Graph-Based Network Intrusion Detection System (NIDS)

A real-time network intrusion detection system that uses machine learning and dynamic graph analysis to identify potential security threats.

## Architecture

This system implements a multi-container architecture with:

- **Backend (Python/FastAPI)**: Real-time packet capture, ML-based anomaly detection, and graph analysis
- **Frontend (React/D3.js)**: Interactive dashboard for visualizing network graphs and security alerts
- **Docker Compose**: Container orchestration for development and deployment

## Features

### 🔬 ML Services Integration (NEW!)

The system now includes comprehensive machine learning services with adaptive functionality:

#### **Advanced ML Mode**
- **Random Forest Classifier**: Supervised learning for known attack patterns
- **Isolation Forest**: Unsupervised anomaly detection for novel threats
- **Ensemble Predictions**: Combines multiple models for higher accuracy
- **Real-time Training**: Adaptive model updates based on network patterns
- **Feature Importance Analysis**: Understand which network features are most critical

#### **Adaptive Architecture**
- **Auto-Detection**: Automatically detects available ML libraries
- **Graceful Fallbacks**: Falls back to simpler methods if ML libraries unavailable
- **Multiple Modes**: Full ML, Basic ML, Simple Rule-based, and Minimal modes
- **Performance Monitoring**: Real-time tracking of prediction accuracy and performance

#### **ML API Endpoints**
- `GET /api/ml/status` - Check ML services status and model information
- `GET /api/ml/feature-importance` - Get feature importance from models
- `POST /api/ml/retrain` - Trigger model retraining
- Real-time ML predictions via WebSocket alerts

### Core Components

1. **Real-Time Traffic Capture**: Uses PyShark for live packet sniffing
2. **Advanced ML Pipeline**: 
   - Multi-model anomaly detection (Random Forest + Isolation Forest)
   - Automatic feature engineering and scaling
   - Confidence scoring and ensemble predictions
   - Fallback to rule-based detection when needed
3. **Dynamic Graph Analysis**: 
   - NetworkX-based graph modeling
   - Centrality analysis for detecting suspicious nodes
   - DBSCAN clustering for topological outliers
4. **Interactive Dashboard**:
   - D3.js force-directed graph visualization
   - Real-time alerts feed via WebSocket
   - JWT-based authentication
   - ML prediction confidence display

### Security Features

- **JWT Authentication**: Secure API access
- **Real-time Alerts**: WebSocket-based alert streaming
- **Graph-based Detection**: Identifies coordinated attacks and unusual communication patterns
- **Multi-model Detection**: Combines supervised and unsupervised ML approaches

## 🚀 Quick Start

### One-Click Launch (Easiest)
1. **Double-click**: `🚀 Start NIDS.bat`
2. **Wait**: Both backend and frontend will start automatically
3. **Access**: Frontend opens at http://localhost:5173, Backend API at http://localhost:8000

### Alternative Launch Methods
- **Full Stack**: `start-app.bat` (Batch) or `start-app.ps1` (PowerShell)
- **Backend Only**: `start-minimal-ml.bat`
- **Stop Services**: `🛑 Stop NIDS.bat`

### Manual Setup (If needed)
```bash
# 1. Setup environment
setup.bat

# 2. Start application  
start-app.bat
```

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Using Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd dynamic-nids-project
   ```

2. **Train ML models** (required on first run):
   ```bash
   cd backend
   python train_models.py
   cd ..
   ```

3. **Start the system**:
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard**:
   - URL: http://localhost:3000
   - Username: `testuser`
   - Password: `testpassword`

### Local Development

1. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python train_models.py
   uvicorn main:app --reload
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Local Development with ML Services

#### **Quick Start Scripts**
```bash
# Test ML dependencies and get recommendations
python backend/test_ml.py

# Auto-start with best available mode
python backend/test_ml.py --auto-start

# Manual mode selection
python backend/main_ml.py      # Full ML mode
python backend/main.py         # Adaptive mode  
python backend/main_simple.py  # Simple mode
python backend/main_minimal.py # Minimal mode
```

#### **Windows Quick Start** 🪟
```bash
# Robust startup with Windows compatibility (RECOMMENDED)
start-robust.bat

# Alternative startup with ML detection
start-with-ml.bat

# Simple mode (no advanced ML)
start-backend-simple.bat

# Minimal mode (no authentication)
start-minimal.bat
```

#### **Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train_models.py
uvicorn main:app --reload
```

## Available Launcher Scripts

### 🚀 Main Launchers
- **`🚀 Start NIDS.bat`** - One-click launcher (recommended)
- **`start-app.bat`** - Full stack startup (Batch)  
- **`start-app.ps1`** - Full stack startup (PowerShell)
- **`🛑 Stop NIDS.bat`** - Stop all services

### 🔧 Backend-Only Scripts
- **`start-minimal-ml.bat`** - Start minimal ML backend only
- **`start-backend-simple.bat`** - Start simple backend without ML

### 📋 Service Management
- **`setup.bat`** - Initial environment setup
- **`install-deps.bat`** - Install all dependencies

---

## API Documentation

Once the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /token`: Authentication (get JWT token)
- `GET /api/graph`: Get current network graph data (protected)
- `GET /users/me`: Get current user info (protected)
- `WebSocket /ws/alerts`: Real-time security alerts
- `GET /api/ml/status`: Check ML services status and model information
- `GET /api/ml/feature-importance`: Get feature importance from models
- `POST /api/ml/retrain`: Trigger model retraining

## Configuration

### Environment Variables

Set in `docker-compose.yml`:

- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `ALGORITHM`: JWT signing algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Network Interface

The system captures packets from the `eth0` interface by default. To change:

1. Update `interface` parameter in `backend/main.py`
2. Ensure the interface exists in your container/environment

## Security Considerations

### Development vs Production

This is a **prototype/development** setup. For production:

1. **Change default credentials**
2. **Use environment-specific secrets**
3. **Configure proper network interfaces**
4. **Set up proper TLS/SSL**
5. **Use production-grade databases**
6. **Implement proper logging and monitoring**

### Network Permissions

The backend container requires elevated network capabilities (`NET_RAW`, `NET_ADMIN`) for packet capture. This is configured in `docker-compose.yml`.

## Development

### Project Structure

```
dynamic-nids-project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── sniffer.py           # Packet capture
│   ├── processor.py         # Feature extraction
│   ├── detector.py          # ML anomaly detection
│   ├── graph_manager.py     # Dynamic graph management
│   ├── graph_analyzer.py    # Graph-based analysis
│   ├── auth.py              # JWT authentication
│   ├── train_models.py      # ML model training
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Application pages
│   │   └── App.jsx          # Main application
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

### Adding New Features

1. **New ML Models**: Extend `detector.py` and update `train_models.py`
2. **Graph Analysis**: Add new algorithms to `graph_analyzer.py`
3. **Frontend Components**: Add to `src/components/`
4. **API Endpoints**: Extend `main.py` with new routes

## Troubleshooting

### Common Issues

1. **Models not found**: Run `python train_models.py` in the backend directory
2. **Permission denied (packet capture)**: Ensure Docker has necessary privileges
3. **WebSocket connection failed**: Check if backend is running and accessible
4. **Authentication errors**: Verify JWT token and credentials

### Logs

View container logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

## Performance Considerations

- Graph pruning runs every 2.5 minutes (TTL/2) to manage memory
- Analysis runs every 15 seconds for real-time detection
- WebSocket connections are managed automatically
- D3.js simulation uses force-directed layout for optimal visualization

## License

This project is for educational and research purposes. Please ensure compliance with local network monitoring regulations.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## References

The system design is based on modern NIDS architecture principles and incorporates:
- Real-time packet analysis techniques
- Graph-based network security analysis
- Machine learning for anomaly detection
- Modern web application architecture with React and FastAPI

## ML Services Modes

### Mode Selection Guide

| Mode | Requirements | Features | Use Case |
|------|-------------|----------|----------|
| **Full ML** | pandas, scikit-learn | Advanced ML models, ensemble predictions, model training | Production environments |
| **Adaptive** | Basic dependencies | Auto-detects ML availability, falls back gracefully | Development, testing |
| **Simple** | FastAPI only | Rule-based detection, statistical analysis | Resource-constrained environments |
| **Minimal** | FastAPI only | Basic functionality, no authentication | Quick demos, troubleshooting |

### ML Performance Benchmarks

- **Prediction Latency**: < 1ms per packet
- **Memory Usage**: 50-200MB (model-dependent)
- **Training Time**: 30-60 seconds for 10K samples
- **Packet Processing**: Up to 10,000 packets/second

### ML Dependencies Installation

```bash
# Core ML dependencies
pip install pandas==2.1.4 scikit-learn==1.4.0 numpy joblib

# If installation fails, try older versions
pip install pandas==1.5.3 scikit-learn==1.3.0

# For Python 3.13 compatibility issues
pip install --only-binary=all pandas scikit-learn
```

## Troubleshooting

#### **Windows Compatibility** ⚠️
- **Robust ML Services**: Handles Windows numpy/pandas compatibility issues
- **Warning Suppression**: Automatically suppresses experimental numpy warnings
- **Graceful Fallbacks**: Falls back to simpler methods if ML libraries fail
- **Safe Startup Scripts**: Windows-specific scripts that handle dependency issues
- **Multiple Modes**: Robust, Simple, and Minimal modes for different environments

#### **ML API Endpoints**
- `GET /api/ml/status` - Check ML services status and model information
- `GET /api/ml/feature-importance` - Get feature importance from models
- `POST /api/ml/retrain` - Trigger model retraining
- Real-time ML predictions via WebSocket alerts
