@echo off
cd /d "c:\Users\Cleo\Desktop\SIH25\backend"
C:\Users\Cleo\Desktop\SIH25\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload