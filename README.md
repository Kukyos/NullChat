# SIH25 Multilingual College Chatbot

A complete multilingual chatbot solution for college websites that answers student questions using Gemini AI and Google Translate. Features dynamic language support, session management, and an animated chat interface.

## Stack
- Backend: FastAPI (Python), Uvicorn, Gemini AI, Google Translate
- Frontend: React + Vite (Custom Chat Widget)
- Database: SQLite with SQLAlchemy
- AI: Google Generative AI (gemini-1.5-flash)
- Languages: English, Hindi, Tamil, Marwari (100+ via Google Translate)

## Quick Start

### 🚀 One-Click Launch (Recommended)
**Windows:** Double-click `start_servers.bat`
**Linux/Mac:** Run `./start_servers.sh`

This automatically starts both servers and opens the chatbot in your browser!

### Manual Setup (Alternative)

#### 1) Backend (FastAPI)
```powershell
cd backend
C:\Users\Cleo\Desktop\SIH25\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2) Frontend (React + Vite)
```powershell
cd frontend
npx vite --port 5173
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000/docs (Swagger)

The frontend calls the backend at `http://localhost:8000`. If you use different ports, update `VITE_API_BASE` in `.env` and restart the dev server.

## Features ✨
- **Multilingual Support**: English, Hindi, Tamil, Marwari + 100+ languages
- **Dynamic Language Selector**: Changes welcome messages based on selected language
- **Smart AI Responses**: Gemini AI handles mixed language queries naturally
- **Session Management**: Maintains conversation context
- **Animated UI**: Black/white theme with loading animations and glow effects
- **College-Specific**: Optimized for admission, fees, hostel, and exam queries

## Test Sample Queries
- "What are the admission requirements?"
- "Hostel fees kya hai?"
- "தேர்வு கால அட்டவணை எப்போது?"
- "College में कैसे admission लेना है?"

## API Testing
```powershell
$body = @{ question = "What are hostel fees?"; session_id = "test123" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method POST -ContentType 'application/json' -Body $body
```

## Roadmap 🗺️
- ✅ Multilingual chat with Gemini AI
- ✅ Dynamic language welcome messages  
- ⏳ PDF document processing pipeline
- ⏳ Voice input/output integration
- ⏳ Admin panel for content management

---

Troubleshooting:
- If PowerShell blocks scripts, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- If `pip` fails SSL, try: `python -m pip install --upgrade pip` then retry.
