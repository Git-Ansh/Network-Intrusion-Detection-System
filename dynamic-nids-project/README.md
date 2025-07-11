# 🛡️ Dynamic Graph-Based Network Intrusion Detection System (NIDS)

A real-time network intrusion detection system that uses machine learning and dynamic graph analysis to identify potential security threats.

## 🚀 Quick Start

### **🎯 One-Click Launch (Recommended)**

1. **Double-click**: `🚀 Start NIDS.bat`
2. **Login** with: `admin` / `admin123`
3. **Access**: http://localhost:5173 (Frontend) & http://localhost:8000 (Backend API)

### **Demo Credentials**
- **Username**: `admin`
- **Password**: `admin123`

## 🏗️ Architecture

This system implements a streamlined Windows-focused architecture with:

- **Backend (Python/FastAPI)**: Real-time packet capture, ML-based anomaly detection, and graph analysis with authentication
- **Frontend (React/D3.js)**: Interactive dashboard for visualizing network graphs and security alerts
- **Windows Batch Launchers**: Simple one-click startup and management

## ✨ Features

### 🔬 **Machine Learning Integration**

#### **Adaptive ML Architecture**
- **Windows-Compatible**: No numpy/sklearn dependencies - works on any Windows system
- **Rule-Based Detection**: Intelligent pattern recognition for anomaly detection
- **Auto-Detection**: Automatically detects available ML libraries and adapts
- **Graceful Fallbacks**: Falls back to simpler methods if advanced ML unavailable
- **Real-time Analysis**: Live packet analysis and scoring

#### **Detection Capabilities**
- **Port-based Detection**: Identifies suspicious port usage
- **Packet Size Analysis**: Detects unusual packet sizes
- **Timing Analysis**: Identifies rapid-fire or unusual timing patterns
- **Protocol Analysis**: TCP/UDP/ICMP pattern recognition
- **Confidence Scoring**: Numerical confidence levels for each detection

#### **ML API Endpoints**
- `GET /api/ml/status` - Check ML services status and model information
- `POST /api/ml/predict` - Submit network data for analysis
- `GET /api/ml/test` - Test detection with sample data
- Real-time ML predictions via WebSocket alerts

### 🔐 **Authentication System**
- **JWT-based Authentication**: Secure token-based login system
- **Protected Endpoints**: All sensitive API endpoints require authentication
- **Session Management**: Automatic token refresh and logout handling
- **Demo Credentials**: `admin` / `admin123` for quick testing

### 📊 **Real-Time Dashboard**
- **Interactive Network Graph**: D3.js-powered visualization of network topology
- **Live Alerts Feed**: Real-time WebSocket-based alert notifications
- **System Statistics**: Node counts, edge counts, and connection status
- **Responsive Design**: Works on desktop and mobile devices

### 🌐 **Core Components**

1. **Real-Time Traffic Analysis**: 
   - Advanced packet feature extraction
   - Multi-pattern anomaly detection
   - Confidence-based scoring system
   
2. **Dynamic Graph Visualization**:
   - Interactive force-directed graph layout
   - Real-time node and edge updates
   - Color-coded threat level indicators
   
3. **Alert System**:
   - WebSocket-based real-time alerts
   - Severity classification
   - Historical alert tracking

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **Windows OS** (optimized for Windows)

### **🚀 Quick Setup**

1. **Run Setup**: `setup.bat` (handles everything automatically)
2. **Start Application**: `🚀 Start NIDS.bat`
3. **Login**: Use `admin` / `admin123`

### **Manual Setup** (if needed)

```cmd
# 1. Clone the repository
git clone <repository-url>
cd dynamic-nids-project

# 2. Run setup script
setup.bat

# 3. Start the application
🚀 Start NIDS.bat
```

## 🎮 Usage

### **Launcher Scripts**

#### **🚀 Start NIDS.bat** (Recommended - One-Click Solution)
- **What it does**: Starts everything automatically
- **Features**:
  - Auto-setup if needed
  - Starts backend (Python/FastAPI) 
  - Starts frontend (React/Vite)
  - Creates separate terminal windows
  - Auto-opens browser

#### **🛑 Stop NIDS.bat**
- **What it does**: Cleanly stops all NIDS services
- **Features**:
  - Stops all Python processes (backend)
  - Stops all Node.js processes (frontend)
  - Checks port availability

### **Manual Control**

```cmd
# Start backend only
cd backend
python main_ml_with_auth.py

# Start frontend only  
cd frontend
npm run dev
```

### **Access Points**
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Login**: admin / admin123

## 🔧 API Endpoints

### **Authentication**
- `POST /token` - Login endpoint (username/password → JWT token)
- `GET /users/me` - Get current user information

### **Graph Data**
- `GET /api/graph` - Get network graph data (nodes & edges)
- `GET /api/graph/data` - Alternative graph endpoint

### **Machine Learning**
- `GET /api/ml/status` - ML services status and model info
- `POST /api/ml/predict` - Submit data for anomaly detection
- `GET /api/ml/test` - Test detection with sample data

### **Alerts & Statistics**
- `GET /api/alerts` - Get recent alerts
- `GET /api/stats` - System statistics
- `WebSocket /ws/alerts` - Real-time alert stream
- `WebSocket /ws` - General real-time updates

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Python Dependencies Issues**
```cmd
# Solution: Recreate virtual environment
python -m venv nids_env
nids_env\Scripts\activate.bat
pip install -r backend\requirements.txt
```

#### **2. Port Already in Use**
```cmd
# Check ports
netstat -an | findstr :8000
netstat -an | findstr :5173

# Kill processes if needed
taskkill /f /im python.exe
taskkill /f /im node.exe
```

#### **3. Frontend Build Issues**
```cmd
# Solution: Clear cache and reinstall
cd frontend
rmdir /s node_modules
del package-lock.json
npm install
npm run dev
```

#### **4. Authentication 404 Errors**
- **Cause**: Using wrong backend file
- **Solution**: Ensure using `main_ml_with_auth.py` (not `main_ml_minimal.py`)

#### **5. Dashboard TypeError**
- **Cause**: Data structure mismatch between backend/frontend
- **Status**: ✅ **FIXED** - Dashboard now safely handles all data structures

### **Network Interface Issues**
- System auto-detects network interfaces
- On Windows: tries Wi-Fi, Ethernet, then defaults to 'Wi-Fi'
- Run with administrator privileges if permission denied

### **Browser Issues**
- **Clear browser cache** if seeing old versions
- **Try incognito mode** to bypass cache
- **Check JavaScript console** for error details

## 🏗️ Project Structure

```
dynamic-nids-project/
├── 🚀 Start NIDS.bat          # Main launcher
├── 🛑 Stop NIDS.bat           # Stop all services  
├── setup.bat                   # Setup script
├── start-app.bat              # Alternative launcher
├── install-deps.bat           # Dependency installer
├── backend/
│   ├── main_ml_with_auth.py   # Main backend (with auth)
│   ├── ml_services_minimal.py # ML services (Windows-compatible)
│   ├── simple_detector_nonumpy.py # Anomaly detector
│   ├── requirements.txt       # Python dependencies
│   └── test_*.py             # Test scripts
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React app
│   │   ├── pages/
│   │   │   ├── Login/        # Login page
│   │   │   └── Dashboard/    # Main dashboard
│   │   └── components/
│   │       ├── NetworkGraph/ # D3.js graph component
│   │       └── AlertsFeed/   # Real-time alerts
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Vite configuration
└── nids_env/                 # Python virtual environment
```

## 🔬 Technical Details

### **Backend Technology Stack**
- **FastAPI**: Modern Python web framework
- **JWT Authentication**: Secure token-based auth
- **WebSocket**: Real-time communication
- **Windows-Compatible ML**: No external ML library dependencies

### **Frontend Technology Stack**  
- **React 18**: Modern UI framework
- **D3.js**: Advanced data visualization
- **Vite**: Fast development and build tool
- **Axios**: HTTP client for API communication

### **ML Detection Methods**
- **Port Analysis**: Detects suspicious port usage (1337, 4444, etc.)
- **Packet Size Analysis**: Identifies unusually large/small packets
- **Timing Analysis**: Detects rapid-fire connections
- **Protocol Patterns**: TCP/UDP/ICMP behavior analysis
- **Confidence Scoring**: 0-100 confidence levels

## 🚨 Recent Fixes & Improvements

### ✅ **Authentication Issue - RESOLVED**
- **Problem**: 404 errors on `/token` endpoint
- **Solution**: Created `main_ml_with_auth.py` with full authentication
- **Status**: All login functionality working

### ✅ **Dashboard TypeError - RESOLVED**  
- **Problem**: `Cannot read properties of undefined (reading 'length')`
- **Root Cause**: Backend returns `edges`, frontend expected `links`
- **Solution**: Added data transformation and safe property access
- **Status**: Dashboard loads without errors

### ✅ **Frontend 404 Errors - RESOLVED**
- **Problem**: Missing API endpoints causing 404s
- **Solution**: Added all required endpoints (`/api/graph`, `/api/alerts`, etc.)
- **Status**: All frontend requests working

### ✅ **Windows Compatibility - ACHIEVED**
- **Problem**: ML libraries not available on all Windows systems
- **Solution**: Created Windows-compatible ML services without numpy/sklearn
- **Status**: Works on any Windows system

## 🎯 Development Status

### **✅ Completed Features**
- [x] Real-time authentication system
- [x] Interactive network graph visualization  
- [x] Windows-compatible ML anomaly detection
- [x] WebSocket-based real-time alerts
- [x] One-click launcher system
- [x] Comprehensive error handling
- [x] API documentation
- [x] Safe data handling in frontend

### **🔄 Current Capabilities**
- Real-time network data visualization
- JWT-based secure authentication
- ML-powered anomaly detection (Windows-compatible)
- Interactive D3.js graph with live updates
- WebSocket alerts and notifications
- Comprehensive API with documentation

### **🚀 Ready for Use**
The system is fully functional and ready for:
- Network monitoring and visualization
- Anomaly detection and alerting
- Real-time threat analysis
- Educational and research purposes
- Further development and customization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the browser console for error details
4. Ensure all prerequisites are installed

---

**🎉 The NIDS system is ready to protect your network!**
