# Launch Script for React + FastAPI CTDI Studio
$env:KMP_DUPLICATE_LIB_OK = "TRUE"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching CTDI Air Pollution Imputation Studio" -ForegroundColor Cyan
Write-Host "  Backend: FastAPI (Port 8000) | Frontend: React (Port 5173)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in new window
Write-Host "[1/3] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process py -ArgumentList "-3.13", "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"

Start-Sleep -Seconds 2

# 2. Start React Frontend in new window
Write-Host "[2/3] Starting React Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory "$PSScriptRoot\frontend"

Start-Sleep -Seconds 3

# 3. Open default browser
Write-Host "[3/3] Opening Studio in browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "`nStudio is up and running! To stop services, close the backend and frontend terminal windows." -ForegroundColor Cyan
