# Dynamic Graph-Based Network Intrusion Detection System (NIDS)

A real-time network intrusion detection system that uses machine learning and dynamic graph analysis to identify potential security threats.

## Architecture

This system implements a multi-container architecture with:

- **Backend (Python/FastAPI)**: Real-time packet capture, ML-based anomaly detection, and graph analysis
- **Frontend (React/D3.js)**: Interactive dashboard for visualizing network graphs and security alerts
- **Docker Compose**: Container orchestration for development and deployment

## Features

### Core Components

1. **Real-Time Traffic Capture**: Uses PyShark for live packet sniffing
2. **ML-Based Anomaly Detection**: 
   - Random Forest (supervised) for known attack patterns
   - Isolation Forest (unsupervised) for novel anomalies
3. **Dynamic Graph Analysis**: 
   - NetworkX-based graph modeling
   - Centrality analysis for detecting suspicious nodes
   - DBSCAN clustering for topological outliers
4. **Interactive Dashboard**:
   - D3.js force-directed graph visualization
   - Real-time alerts feed via WebSocket
   - JWT-based authentication

### Security Features

- **JWT Authentication**: Secure API access
- **Real-time Alerts**: WebSocket-based alert streaming
- **Graph-based Detection**: Identifies coordinated attacks and unusual communication patterns
- **Multi-model Detection**: Combines supervised and unsupervised ML approaches

## Quick Start

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

## API Documentation

Once the backend is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /token`: Authentication (get JWT token)
- `GET /api/graph`: Get current network graph data (protected)
- `GET /users/me`: Get current user info (protected)
- `WebSocket /ws/alerts`: Real-time security alerts

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
