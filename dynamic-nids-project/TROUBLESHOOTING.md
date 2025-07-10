# NIDS Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker Desktop Not Running

**Error**: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**Solutions**:
1. **Start Docker Desktop**:
   - Open Docker Desktop from Start menu
   - Wait for it to fully initialize (green status)
   - Try `docker-compose up --build` again

2. **Run locally instead** (if Docker issues persist):
   ```cmd
   run-local.bat
   ```

### 2. Python Dependencies Issues

**Error**: Import errors or module not found

**Solutions**:
```cmd
# Create fresh virtual environment
python -m venv nids_env
nids_env\Scripts\activate.bat
pip install -r backend\requirements.txt
```

### 3. Network Interface Detection

**Error**: Interface not found or permission denied

**Solutions**:
- The system now auto-detects network interfaces
- On Windows, it will try Wi-Fi, Ethernet, then fallback to 'Wi-Fi'
- For Docker: Run with administrator privileges if needed

### 4. Port Already in Use

**Error**: Port 8000 or 3000 already in use

**Solutions**:
```cmd
# Kill processes using the ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### 5. WebSocket Connection Failed

**Error**: WebSocket connection issues in frontend

**Solutions**:
1. Ensure backend is running on port 8000
2. Check firewall settings
3. Verify CORS configuration

### 6. ML Models Not Found

**Error**: Model files not found

**Solutions**:
```cmd
cd backend
python train_models.py
```

## Running Options

### Option 1: Docker (Full System)
```cmd
# Ensure Docker Desktop is running
docker-compose up --build
```
Access: http://localhost:3000

### Option 2: Local Development
```cmd
# Use the local runner script
run-local.bat
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Option 3: Manual Setup
```cmd
# Backend
cd backend
python -m venv nids_env
nids_env\Scripts\activate.bat
pip install -r requirements.txt
python train_models.py
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Default Credentials
- Username: `testuser`
- Password: `testpassword`

## Important Notes

### For Local Development
- PyShark requires WinPcap or Npcap on Windows
- May need to run as administrator for packet capture
- Some features may be limited without proper network permissions

### For Production
- Change default credentials
- Use environment-specific secrets
- Configure proper network interfaces
- Set up TLS/SSL

## Network Interface Detection

The system automatically detects available network interfaces:

1. **Windows**: Looks for active Ethernet/Wi-Fi interfaces
2. **Linux/Mac**: Defaults to eth0
3. **Fallback**: Uses 'Wi-Fi' on Windows, 'eth0' elsewhere

To manually specify an interface, edit `backend/main.py`:
```python
traffic_snffr = TrafficSniffer(interface='your-interface-name', ...)
```

## Logs and Debugging

### Backend Logs
- Console output shows startup messages
- Interface detection info
- Alert notifications

### Frontend Logs
- Browser developer console
- Network tab for API calls
- WebSocket connection status

### Docker Logs
```cmd
docker-compose logs backend
docker-compose logs frontend
```

## Performance Tips

1. **Graph Size**: System automatically prunes old nodes/edges
2. **Memory Usage**: Restart if running for extended periods
3. **Packet Volume**: High traffic may impact performance
4. **Browser**: Use modern browsers for best D3.js performance

## Contact/Support

For additional issues:
1. Check the README.md for detailed setup instructions
2. Review PROJECT_STATUS.md for implementation details
3. Examine console/log outputs for specific error messages
