# 🚀 NIDS Full Stack Launcher - Quick Guide

## 📋 What Was Created

I've created a comprehensive set of launcher scripts that make it incredibly easy to start both the backend and frontend of your NIDS application with just one click!

## 🎯 Main Launchers

### 1. **🚀 Start NIDS.bat** (Recommended - One-Click Solution)

- **What it does**: Starts everything automatically
- **How to use**: Just double-click this file
- **Features**:
  - Auto-setup if needed
  - Starts backend (Python/FastAPI)
  - Starts frontend (React/Vite)
  - Opens browser automatically
  - Creates separate terminal windows for each service

### 2. **start-app.bat** (Full Control)

- **What it does**: Comprehensive startup with status checks
- **Features**:
  - Detailed progress reporting
  - Prerequisites checking
  - Automatic dependency installation
  - Service health testing
  - Browser launch

### 3. **start-app.ps1** (PowerShell Version)

- **What it does**: Same as start-app.bat but with PowerShell features
- **Features**:
  - Enhanced error handling
  - Better status reporting
  - Automatic cleanup
  - Colored output

## 🛑 Service Management

### **🛑 Stop NIDS.bat**

- **What it does**: Cleanly stops all NIDS services
- **Features**:
  - Stops all Python processes (backend)
  - Stops all Node.js processes (frontend)
  - Checks port availability
  - Confirms shutdown

## 🔧 Technical Details

### Services Started:

1. **Backend Server**

   - Location: `backend/main_ml_minimal.py`
   - Port: 8000
   - Features: ML-enabled anomaly detection, REST API
   - URLs:
     - API: http://localhost:8000
     - Docs: http://localhost:8000/docs

2. **Frontend Server**
   - Location: `frontend/`
   - Port: 5173
   - Features: React dashboard, real-time graphs
   - URL: http://localhost:5173

### Automatic Features:

- ✅ Virtual environment activation
- ✅ Dependency checking and installation
- ✅ Service health monitoring
- ✅ Browser launching
- ✅ Error handling and recovery
- ✅ Clean shutdown

## 📖 Usage Instructions

### First Time Setup:

1. **Double-click** `🚀 Start NIDS.bat`
2. **Wait** for automatic setup and service startup
3. **Use** the application that opens in your browser

### Daily Usage:

1. **Double-click** `🚀 Start NIDS.bat`
2. **Access** your NIDS dashboard immediately

### To Stop:

1. **Double-click** `🛑 Stop NIDS.bat`
2. **Or** close the terminal windows manually

## 🎉 What This Achieves

### For Users:

- **Zero-Configuration**: Just double-click to start
- **Automatic Setup**: No manual environment management
- **Instant Access**: Browser opens automatically
- **Easy Shutdown**: One-click service stopping

### For Developers:

- **Separate Windows**: Backend and frontend in their own terminals
- **Live Logs**: See real-time service output
- **Easy Debugging**: Individual service control
- **Clean Environment**: Proper environment variable setup

## 🌟 Summary

You now have a **professional-grade application launcher** that:

1. **🎯 Starts everything** with one double-click
2. **🔧 Handles setup** automatically
3. **🌐 Opens browser** to the right URLs
4. **📊 Shows status** of all services
5. **🛑 Stops cleanly** when needed

### Quick Commands:

- **Start Everything**: Double-click `🚀 Start NIDS.bat`
- **Stop Everything**: Double-click `🛑 Stop NIDS.bat`
- **Frontend Only**: `cd frontend && npm run dev`
- **Backend Only**: `start-minimal-ml.bat`

## 🎊 Ready to Use!

Your NIDS application now has a **complete startup solution** that makes it as easy to launch as any commercial software. Just double-click and go! 🚀
