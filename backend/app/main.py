from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .models.database import Conversation
from .services.chat_pipeline import process_question
from .services.voice_sarvam import router as voice_router
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="SIH Bot API", version="0.1.0")

# Initialize database tables
init_db()

# Mount voice (Sarvam placeholder) router
app.include_router(voice_router)

# Allow local dev frontends - wildcard for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Serve uploaded files - disabled for now
# app.mount("/files", StaticFiles(directory="data"), name="files")

# Request/Response models
class AskRequest(BaseModel):
    question: str
    session_id: str | None = None
    language: str = "auto"

class AskResponse(BaseModel):
    answer: str
    confidence: float = 0.0
    language_detected: str = "en"
    session_id: str
    conversation_id: int = None

class FeedbackRequest(BaseModel):
    conversation_id: int
    feedback: int  # -1, 0, 1

class ForwardRequest(BaseModel):
    conversation_id: int
    additional_context: str = ""


@app.get("/", response_class=HTMLResponse)
def root(_: Request):
        return """
        <!doctype html>
        <html>
            <head>
                <meta charset='utf-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1'>
                <title>College Chatbot</title>
                <style>
                    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem}
                    h1{font-size:1.4rem}
                    form{display:flex;gap:.5rem;margin:.5rem 0}
                    input,button{padding:.6rem;font-size:1rem}
                    .log{white-space:pre-wrap;background:#fafafa;border:1px solid #eee;padding:1rem;border-radius:8px}
                </style>
            </head>
            <body>
                <h1>College Chatbot (basic UI)</h1>
                <p>If the React app isn't running, you can use this simple tester.</p>
                <form id="f">
                    <input id="q" placeholder="Ask a question..." style="flex:1"/>
                    <button>Ask</button>
                </form>
                <div class="log" id="log"></div>
                <script>
                    const f=document.getElementById('f');
                    const q=document.getElementById('q');
                    const log=document.getElementById('log');
                    f.addEventListener('submit', async (e)=>{
                        e.preventDefault();
                        const question=q.value.trim();
                        if(!question) return;
                        log.textContent = 'Asking...';
                        try{
                            const res = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question})});
                            const data = await res.json();
                            log.textContent = data.answer || JSON.stringify(data,null,2);
                        }catch(err){ log.textContent = String(err); }
                    });
                </script>
            </body>
        </html>
        """

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_db)):
    pipeline_result = process_question(
        question=req.question,
        incoming_language=req.language,
        session_id=req.session_id,
        db=db,
    )
    return AskResponse(
        answer=pipeline_result["answer"],
        confidence=pipeline_result["confidence"],
        language_detected=pipeline_result["language_detected"],
        session_id=pipeline_result["session_id"],
        conversation_id=pipeline_result["conversation_id"],
    )

@app.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.feedback = req.feedback
    db.commit()
    
    return {"success": True, "message": "Feedback recorded"}

@app.post("/forward-to-admin")
def forward_to_admin(req: ForwardRequest, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.forwarded_to_admin = True
    if req.additional_context:
        conversation.admin_response = f"User context: {req.additional_context}"
    db.commit()
    
    return {"success": True, "message": "Question forwarded to admin team"}
