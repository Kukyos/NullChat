from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .models.database import Conversation
from .services.groq_service import groq_service
from .services.translation import translator_service
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

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
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

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_db)):
    # Generate session ID if not provided
    session_id = req.session_id or str(uuid.uuid4())
    
    logger.info(f"Processing question: '{req.question}' | incoming language: '{req.language}'")

    # 1. Detect user language
    user_lang = req.language if req.language != "auto" else translator_service.detect_language(req.question)
    logger.info(f"Language debug | incoming: '{req.language}' | detected: '{user_lang}'")

    # 2. If Hindi/Marwari, translate input to English, get Romanized Hindi from Groq, return as-is
    if user_lang in ("hi", "mwr"):
        question_en = translator_service.translate_to_english(req.question, source_lang=user_lang) if user_lang != "en" else req.question
        try:
            llm_response = groq_service.generate_response(question_en, response_language=user_lang)
            answer_user_lang = llm_response["answer"]  # Already Romanized Hindi
            result = {
                "answer": answer_user_lang,
                "confidence": llm_response.get("confidence", 0.8),
                "language_detected": user_lang,
                "source": "groq-ai"
            }
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            result = {
                "answer": error_details,
                "confidence": 0.1,
                "language_detected": user_lang,
                "source": "error"
            }
    else:
        # All other languages: translate input to English, get English from Groq, translate to user language
        question_en = translator_service.translate_to_english(req.question, source_lang=user_lang) if user_lang != "en" else req.question
        try:
            llm_response = groq_service.generate_response(question_en, response_language="en")
            answer_en = llm_response["answer"]
            logger.info(f"Groq answer (EN): {answer_en}")
            if user_lang != "en":
                answer_user_lang = translator_service.translate_from_english(answer_en, target_lang=user_lang)
                logger.info(f"Translated answer to user language: {answer_user_lang}")
            else:
                answer_user_lang = answer_en
            result = {
                "answer": answer_user_lang,
                "confidence": llm_response.get("confidence", 0.8),
                "language_detected": user_lang,
                "source": "groq-ai"
            }
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            result = {
                "answer": error_details,
                "confidence": 0.1,
                "language_detected": user_lang,
                "source": "error"
            }

    # Save conversation to database
    conversation = Conversation(
        session_id=session_id,
        user_message=req.question,
        bot_response=result["answer"],
        language_detected=result["language_detected"],
        confidence_score=result["confidence"]
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)  # Get the ID

    return AskResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        language_detected=result["language_detected"],
        session_id=session_id,
        conversation_id=conversation.id
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
