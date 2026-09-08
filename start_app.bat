@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
echo ========================================================
echo   Launching CTDI Air Pollution Imputation Studio (React + FastAPI)
echo ========================================================

echo 1. Starting FastAPI Backend on http://127.0.0.1:8000...
start "CTDI Backend (FastAPI)" py -3.13 -m uvicorn api:app --host 127.0.0.1 --port 8000

echo 2. Starting React Frontend on http://localhost:5173...
cd frontend
start "CTDI Frontend (React)" npm run dev
cd ..

timeout /t 3 /nobreak >nul
echo 3. Opening Studio in your default browser...
start http://localhost:5173

echo.
echo All services launched! You can now use the React dashboard.
