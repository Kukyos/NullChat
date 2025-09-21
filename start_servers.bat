@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo Starting SIH25 Multilingual College Chatbot...
echo.

REM Resolve repo-root relative to this script
set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "BACKEND_ENV=%BACKEND_DIR%\.env"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

REM Kill any existing processes on the ports
echo Stopping existing servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a >nul 2>&1

echo.
REM Ensure GROQ_API_KEY is available; prompt if missing (local interactive only)
if "%GROQ_API_KEY%"=="" (
	echo GROQ_API_KEY is not set. Please paste your Groq API key.
	set /p GROQ_API_KEY=GROQ_API_KEY: 
)

REM Ensure backend/.env exists and contains GROQ_API_KEY (append/replace key)
if not exist "%BACKEND_DIR%" (
	echo ERROR: Backend directory not found at "%BACKEND_DIR%".
	goto end
)
if not exist "%BACKEND_ENV%" (
	echo Creating backend .env file...
	> "%BACKEND_ENV%" echo GROQ_API_KEY=%GROQ_API_KEY%
) else (
	REM Remove any existing GROQ_API_KEY lines and append the current value
	findstr /v /b /i "GROQ_API_KEY=" "%BACKEND_ENV%" > "%BACKEND_ENV%.tmp"
	>> "%BACKEND_ENV%.tmp" echo GROQ_API_KEY=%GROQ_API_KEY%
	move /Y "%BACKEND_ENV%.tmp" "%BACKEND_ENV%" >nul
)

REM Select Python command: prefer venv, else py, else python
set "PY_EXE="
set "PY_ARGS="
if exist "%VENV_PY%" (
	set "PY_EXE=%VENV_PY%"
) else (
	where py >nul 2>&1 && ( set "PY_EXE=py" & set "PY_ARGS=-3" )
	if "%PY_EXE%"=="" (
		where python >nul 2>&1 && set "PY_EXE=python"
	)
)
if "%PY_EXE%"=="" (
	echo ERROR: Could not find Python. Please install Python 3.10+ or create .venv.
	goto end
)

:start_servers
echo Starting Backend Server (FastAPI)...
cd /d "%BACKEND_DIR%"
start "Backend Server" cmd /k ""%PY_EXE%" %PY_ARGS% -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server (Vite)...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
	echo Installing frontend dependencies (first run)...
	call npm install
)
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

:end
endlocal