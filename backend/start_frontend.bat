@echo off
setlocal

set "FRONTEND_DIR=%~dp0..\frontend"
cd /d "%FRONTEND_DIR%"

where npm >nul 2>&1
if errorlevel 1 (
	echo npm not found. Please install Node.js from https://nodejs.org to run the Vite dev server.
	exit /b 1
)

if not exist node_modules (
	echo Installing frontend dependencies...
	call npm install
)

start cmd /k "npm run dev"

endlocal