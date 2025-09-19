@echo off
echo Starting SIH25 Multilingual College Chatbot...
echo.

REM Kill any existing processes on the ports
echo Stopping existing servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a >nul 2>&1

echo.
echo Starting Backend Server (FastAPI)...
cd /d "C:\Users\Cleo\Desktop\SIH25\backend"
start "Backend Server" cmd /k ""C:\Users\Cleo\Desktop\SIH25\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server (Vite)...
cd /d "C:\Users\Cleo\Desktop\SIH25\frontend"
start "Frontend Server" cmd /k npx vite --port 5173

echo.
echo ========================================
echo   SIH25 Chatbot Servers Started!
echo ========================================
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to open the chatbot in browser...
pause >nul
start http://localhost:5173

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause