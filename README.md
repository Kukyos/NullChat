# SIH25 Multilingual College Chatbot

A complete multilingual chatbot solution for college websites that answers student questions using LLMs (currently Groq + Gemini capable) and Google Translate. Features dynamic language support, session management, real Sarvam voice mode, and an animated chat interface.

## Stack
- Backend: FastAPI (Python), Uvicorn, Groq or Gemini AI, Google Translate
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
- **Multilingual Support**: English, Hindi, Tamil, Marwari + 100+ languages (auto-detect)
- **Romanized Hindi / Marwari**: Special handling returns readable Latin script
- **Dynamic Language Selector**: Changes welcome messages based on selected language
- **Smart AI Responses**: Current default Groq model (Gemini wiring still available)
- **Session Management**: Maintains conversation context
- **Voice Mode (Real)**: Record audio → Sarvam STT → LLM → Sarvam TTS
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
- ✅ Multilingual chat (Groq + translation)
- ✅ Dynamic language welcome messages  
- ✅ Shared chat pipeline refactor (text + voice reuse)
- ✅ Real Sarvam STT/TTS integration
- ⏳ PDF document processing pipeline
- ⏳ Admin panel for content management
- ⏳ Streaming responses / incremental audio

## Environment Variables
Create or update `backend/.env` (the `start_servers.bat` script auto-injects keys):

```
GROQ_API_KEY=your_groq_key_here
SARVAM_API_KEY=your_sarvam_key_here   # REQUIRED for voice endpoints
GEMINI_API_KEY=your_gemini_key_here   # (optional if enabling Gemini again)
SARVAM_STT_ENDPOINT=https://api.sarvam.ai/v1/audio/transcribe
SARVAM_TTS_ENDPOINT=https://api.sarvam.ai/v1/audio/synthesize
SARVAM_TTS_VOICE=default              # override with a valid Sarvam voice id
SARVAM_TTS_FORMAT=wav                 # desired output format if supported (wav/mp3/...)
SARVAM_TIMEOUT=30                     # request timeout seconds
```

The batch script will:
- Load existing keys from `backend/.env`
- Prompt for missing keys (unless you run with `--no-prompt`)

## Voice Mode (Real Sarvam)
Flow:
1. Browser records audio (WebM) via `MediaRecorder`.
2. Frontend sends the blob to `POST /voice/chat` (field `file`).
3. Backend uploads audio to Sarvam STT -> receives transcript.
4. Transcript is processed through the LLM pipeline (translation, answer, DB logging).
5. Answer text is sent to Sarvam TTS -> receives base64 audio.
6. JSON returned: `{ transcript, answer, confidence, language_detected, conversation_id, audio_base64, audio_format }`.
7. Frontend decodes & plays audio (MIME inferred from `audio_format`).

Requirements:
- `SARVAM_API_KEY` must be set.
- `httpx` must be installed (already in `requirements.txt`).
- Adjust `SARVAM_TTS_VOICE` / `SARVAM_TTS_FORMAT` to match available Sarvam voices & formats.
- For browser recordings (MediaRecorder produces WebM/Opus) install `ffmpeg` on PATH so the backend can transcode to 16kHz mono WAV before STT. Without ffmpeg, raw webm is sent and Sarvam may reject it.

## Running Without Prompts
If you already have keys in `.env` or environment variables:
```
start_servers.bat --no-prompt
```
This skips interactive input and launches directly.

## Switching / Adding Models
- Shared pipeline logic lives in `backend/app/services/chat_pipeline.py`.
- To swap model providers, adjust `groq_service` or add a similar `gemini_service` invocation and route selection flag.

## Minimal API Smoke Test
With backend running and `GROQ_API_KEY` set:
```
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"Hello"}'
```
Voice (real):
```
curl -X POST http://127.0.0.1:8000/voice/chat -F "file=@sample.webm"
```

---

Troubleshooting:
- If PowerShell blocks scripts, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- If `pip` fails SSL, try: `python -m pip install --upgrade pip` then retry.
