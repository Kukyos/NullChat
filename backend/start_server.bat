@echo off
setlocal

REM Resolve backend dir as this script's directory
set "BACKEND_DIR=%~dp0"
set "PY=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%PY%" (
	echo Virtual environment not found. Please run start_servers.bat from repo root to set up and start.
	exit /b 1
)

cd /d "%BACKEND_DIR%"
"%PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

endlocal