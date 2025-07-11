# NIDS Full Stack Startup Script (PowerShell)
# Starts both backend and frontend with proper error handling

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "          NIDS - Full Stack Application Starter" -ForegroundColor Cyan  
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Environment variables
$env:PYTHONWARNINGS = "ignore"
$env:PYTHONPATH = Join-Path $scriptDir "backend"
$env:OMP_NUM_THREADS = "1"

Write-Host "[1/4] Checking Prerequisites..." -ForegroundColor Yellow

# Check Python virtual environment
$venvPath = Join-Path $scriptDir "nids_env\Scripts\activate.bat"
if (-not (Test-Path $venvPath)) {
    Write-Host "[!] Python virtual environment not found." -ForegroundColor Red
    Write-Host "[*] Please run setup.bat first to create the environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check frontend dependencies
$nodeModulesPath = Join-Path $scriptDir "frontend\node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "[*] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location (Join-Path $scriptDir "frontend")
    
    try {
        npm install
        Write-Host "[✓] Frontend dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "[!] Failed to install frontend dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Set-Location $scriptDir
} else {
    Write-Host "[✓] Frontend dependencies found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Starting Backend Server..." -ForegroundColor Yellow

# Start backend in new window
$backendScript = @"
cd /d "$scriptDir\backend"
set PYTHONWARNINGS=ignore
call "$scriptDir\nids_env\Scripts\activate.bat"
echo ================================================================
echo                    NIDS Backend Server
echo ================================================================
echo Starting ML-enabled backend on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop
echo ================================================================
python main_ml_minimal.py
pause
"@

$backendScript | Out-File -FilePath "temp_start_backend.bat" -Encoding ASCII
Start-Process -FilePath "temp_start_backend.bat" -WindowStyle Normal

Write-Host "[✓] Backend starting on http://localhost:8000" -ForegroundColor Green
Write-Host "[*] Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "[3/4] Starting Frontend Server..." -ForegroundColor Yellow

# Start frontend in new window  
$frontendScript = @"
cd /d "$scriptDir\frontend"
echo ================================================================
echo                    NIDS Frontend Server
echo ================================================================
echo Starting React development server on http://localhost:5173
echo Press Ctrl+C to stop
echo ================================================================
npm run dev
pause
"@

$frontendScript | Out-File -FilePath "temp_start_frontend.bat" -Encoding ASCII
Start-Process -FilePath "temp_start_frontend.bat" -WindowStyle Normal

Write-Host "[✓] Frontend starting on http://localhost:5173" -ForegroundColor Green
Write-Host "[*] Waiting for frontend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "[4/4] Opening Application..." -ForegroundColor Yellow

# Wait a bit more for services to fully start
Start-Sleep -Seconds 2

# Open in browser
Start-Process "http://localhost:5173"
Start-Process "http://localhost:8000/docs"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                    🚀 NIDS APPLICATION STARTED" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Frontend (React):     http://localhost:5173" -ForegroundColor White
Write-Host "🔧 Backend API:          http://localhost:8000" -ForegroundColor White  
Write-Host "📚 API Documentation:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                        Service Windows" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Two new command windows have opened:" -ForegroundColor White
Write-Host "  - NIDS Backend Server (Python/FastAPI)" -ForegroundColor White
Write-Host "  - NIDS Frontend Server (React/Vite)" -ForegroundColor White
Write-Host ""
Write-Host "To stop the application:" -ForegroundColor Yellow
Write-Host "  Close both command windows or press Ctrl+C in each" -ForegroundColor White
Write-Host ""

# Test connection
Write-Host "Testing backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[✓] Backend is healthy and responding!" -ForegroundColor Green
    } else {
        Write-Host "[!] Backend responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Backend not responding yet. It may still be starting up." -ForegroundColor Yellow
    Write-Host "    Please wait a moment and check http://localhost:8000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete! You can now close this PowerShell window." -ForegroundColor Green
Write-Host "   The backend and frontend will continue running in their own windows." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

# Cleanup temp files
Remove-Item "temp_start_backend.bat" -ErrorAction SilentlyContinue
Remove-Item "temp_start_frontend.bat" -ErrorAction SilentlyContinue

Read-Host "Press Enter to exit this window"
