#!/bin/bash

echo "Starting SIH25 Multilingual College Chatbot..."
echo

# Kill any existing processes on the ports
echo "Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo
echo "Starting Backend Server (FastAPI)..."
cd "$(dirname "$0")/backend"
source "../.venv/Scripts/activate" 2>/dev/null || source "../.venv/bin/activate"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to initialize..."
sleep 5

echo
echo "Starting Frontend Server (Vite)..."
cd "../frontend"
npx vite --port 5173 &
FRONTEND_PID=$!

echo
echo "========================================"
echo "   SIH25 Chatbot Servers Started!"
echo "========================================"
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173"
echo
echo "Press Ctrl+C to stop both servers..."

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Servers stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Wait for both processes
wait