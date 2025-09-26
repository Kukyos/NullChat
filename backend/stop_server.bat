@echo off
REM Terminates all uvicorn and python processes for backend

taskkill /F /IM uvicorn.exe >nul 2>&1
REM If running as python process (not uvicorn.exe)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.main*" >nul 2>&1

echo All backend server sessions terminated.
pause
