# NIDS Suite - Real-Time Network Intrusion Detection System

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
</p>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🔭 Overview

NIDS Suite is a production-grade, low-latency security platform that captures, analyzes, and visualizes network traffic in real-time. Built using a polyglot, service-oriented architecture, it provides comprehensive intrusion detection capabilities without sacrificing developer ergonomics, horizontal scalability, or user experience.

### Mission Statement

> Deliver a production-grade, low-latency security platform that captures, analyzes, and visualizes every byte in motion across modern networks—without sacrificing developer ergonomics, horizontal scalability, or user experience.

## ✨ Features

- **Real-time Traffic Analysis**: Monitor wire-speed traffic with minimal latency
- **Advanced Threat Detection**: Identify both signature-based and behavior-based threats
- **Interactive Dashboard**: Intuitive web interface for alert management and visualization
- **ML-powered Anomaly Detection**: Leverage Isolation Forest and Random Forest algorithms
- **Scalable Architecture**: Microservices design for horizontal scaling
- **Comprehensive API**: RESTful endpoints for integration with other security tools
- **Role-based Access Control**: Granular permissions with Viewer, Analyst, and Admin roles
- **Exportable Intelligence**: Export alerts in STIX 2.1 format

## 🏗️ Architecture

NIDS Suite implements a polyglot, service-oriented architecture:

- **Node.js (Express 18)**: High-throughput REST API gateway
- **Python 3.11**: Packet capture and machine learning inference
- **Vite 5 + React 18**: Interactive frontend with tailwindCSS
- **Supabase**: Unified backend with PostgreSQL, Authentication, and Realtime subscriptions
- **Socket.io 5**: Bidirectional event streaming for alerts and metrics

### Layered Architecture

| Layer | Component | Technology | Default Port | Responsibilities |
|-------|-----------|------------|--------------|------------------|
| **Presentation** | Frontend | React, TailwindCSS | 3001 | User interface, dashboards, analytics |
| **Gateway/API** | API Gateway | Express, Node.js | 5001 | AuthN/AuthZ, REST endpoints, WebSockets |
| **Processing** | Microservices | Python, Scapy | 5002 | Packet capture, flow analysis |
| **Analytics** | ML Engine | Python, scikit-learn | 5002 (shared) | Anomaly detection, classification |
| **Storage** | Database | Supabase (PostgreSQL) | - | Data persistence, real-time updates |

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase account
- Docker (for deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/acme/nids-suite.git
   cd nids-suite
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Update .env with your Supabase credentials and other settings
   ```

3. Install dependencies:
   ```bash
   # API Gateway
   cd api-gateway
   npm install
   
   # Frontend
   cd ../frontend
   npm install
   
   # Microservices
   cd ../microservices
   pip install -r requirements.txt
   ```

4. Start development servers:
   ```bash
   # API Gateway
   cd api-gateway
   npm run dev
   
   # Frontend
   cd ../frontend
   npm run dev
   
   # Microservices
   cd ../microservices
   python run_all.py
   ```

5. Access the application:
   - Frontend: http://localhost:3001
   - API: http://localhost:5001

## 📁 Project Structure

```
nids-suite
├── .github
│   └── workflows                  # CI/CD pipelines
├── api-gateway                    # Express API server
│   ├── src
│   │   ├── controllers            # Request handlers
│   │   ├── middleware             # Express middleware
│   │   ├── routes                 # API routes
│   │   ├── services               # Business logic
│   │   ├── types                  # TypeScript interfaces
│   │   └── utils                  # Helper functions
├── common                         # Shared code
│   ├── schemas                    # Avro schemas
│   └── types                      # Shared TypeScript interfaces
├── frontend                       # React frontend
│   ├── public                     # Static assets
│   └── src
│       ├── components             # React components
│       ├── contexts               # React contexts
│       ├── hooks                  # Custom hooks
│       ├── pages                  # Page components
│       ├── types                  # TypeScript interfaces
│       └── utils                  # Helper functions
├── microservices                  # Python microservices
│   ├── ml_engine                  # Machine learning services
│   └── packet_capture             # Packet capture and analysis
├── scripts                        # Utility scripts
├── supabase                       # Supabase configuration
│   ├── functions                  # Edge Functions
│   └── migrations                 # Database migrations
└── docker-compose.yml             # Docker configuration
```

## 🔧 Key Components

### API Gateway

The Express-based API Gateway serves as the central access point for the application, handling authentication, authorization, and routing of API calls.

### Frontend Dashboard

The React-based frontend provides an intuitive interface for monitoring network activity, managing alerts, and visualizing threats.

### Packet Capture Service

The Python-based packet capture service monitors network traffic, reconstructs flows, and extracts relevant features for analysis.

### Machine Learning Engine

The ML engine analyzes network traffic patterns to detect anomalies and classify potential threats using Isolation Forest and Random Forest algorithms.

### Supabase Backend

The Supabase backend provides PostgreSQL storage, authentication, real-time subscriptions, and edge functions for seamless data management.

## 💻 Development

### Running in Development Mode

```bash
# Start all services in development mode
npm run dev
```

### Code Style and Linting

```bash
# Run linting
npm run lint

# Run formatting
npm run format
```

## 🧪 Testing

```bash
# Run API Gateway tests
cd api-gateway
npm test

# Run Frontend tests
cd frontend
npm test

# Run Microservice tests
cd microservices
pytest
```

## 📦 Deployment

### Using Docker

```bash
# Build and start all containers
docker-compose up --build
```

### Production Deployment

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy API Gateway and Microservices using Docker:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by the NIDS Suite Team