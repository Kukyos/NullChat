@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
set "FRONTEND_DIR=%ROOT_DIR%\frontend"
set "BACKEND_DIR=%ROOT_DIR%\backend"

REM Prefer running the root launcher when npm is missing (it will fallback to backend UI)
where npm >nul 2>&1
if errorlevel 1 (
	echo Node.js / npm not found. Starting full launcher instead...
	if exist "%ROOT_DIR%\start_servers.bat" (
		call "%ROOT_DIR%\start_servers.bat"
		exit /b 0
	) else (
		echo ERROR: Root launcher not found. Please run start_servers.bat from the project root.
		exit /b 1
	)
)

REM Start backend if it's not already listening on :8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do set "PORT8000=%%a"
if not defined PORT8000 (
	if exist "%BACKEND_DIR%\start_server.bat" (
		echo Backend not running. Starting backend...
		start "Backend Server" cmd /k "%BACKEND_DIR%\start_server.bat"
		timeout /t 4 /nobreak >nul
	)
)

cd /d "%FRONTEND_DIR%"
if not exist node_modules (
	echo Installing frontend dependencies...
	call npm install
)

start "Frontend Server" cmd /k "npm run dev"
start http://localhost:5173

endlocal