"""Shared chat processing pipeline.

Provides a single function `process_question` reused by both text /ask and voice /voice/chat flows.
Encapsulates:
  * Session ID handling
  * Language detection & translation policy (hi/mwr Romanization special case)
  * Groq generation
  * Back-translation where needed
  * Persistence in Conversation table
Returns a dict with keys: answer, confidence, language_detected, session_id, conversation_id.
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy.orm import Session
from ..models.database import Conversation
from .translation import translator_service
from .groq_service import groq_service

logger = logging.getLogger(__name__)

SPECIAL_DIRECT_LANGS = {"hi", "mwr"}

def process_question(*, question: str, incoming_language: str | None, session_id: str | None, db: Session) -> dict:
    session_id = session_id or str(uuid.uuid4())
    # Detect language if auto or not provided
    user_lang = incoming_language if incoming_language and incoming_language != "auto" else translator_service.detect_language(question)
    logger.info(f"[pipeline] Q='{question[:80]}' lang_in='{incoming_language}' lang_det='{user_lang}'")

    try:
        if user_lang in SPECIAL_DIRECT_LANGS:
            # Translate to English ONLY for model context if not already English; request Romanized output in same language
            question_en = translator_service.translate_to_english(question, source_lang=user_lang) if user_lang != "en" else question
            llm_response = groq_service.generate_response(question_en, response_language=user_lang)
            answer_user_lang = llm_response["answer"]
        else:
            question_en = translator_service.translate_to_english(question, source_lang=user_lang) if user_lang != "en" else question
            llm_response = groq_service.generate_response(question_en, response_language="en")
            answer_en = llm_response["answer"]
            answer_user_lang = translator_service.translate_from_english(answer_en, target_lang=user_lang) if user_lang != "en" else answer_en
        confidence = llm_response.get("confidence", 0.8)
        error_mode = False
    except Exception as e:  # Capture stack for debugging but return controlled message
        logger.exception("[pipeline] Generation error")
        answer_user_lang = f"Error: {e}"
        confidence = 0.0
        error_mode = True

    # Persist conversation
    conv = Conversation(
        session_id=session_id,
        user_message=question,
        bot_response=answer_user_lang,
        language_detected=user_lang,
        confidence_score=confidence,
    )
    try:
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id
    except Exception:
        logger.exception("[pipeline] Failed to persist conversation")
        conv_id = None

    return {
        "answer": answer_user_lang,
        "confidence": confidence,
        "language_detected": user_lang,
        "session_id": session_id,
        "conversation_id": conv_id,
        "error": error_mode,
    }
