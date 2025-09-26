"""
Gemini AI service for generating intelligent responses (optional).
This module is not required for core functionality. If configured, it will
use the GEMINI_API_KEY from environment/.env. No keys are hardcoded.
"""
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except Exception:
    genai = None


class GeminiService:
    def __init__(self):
        # Load env from backend/.env if present
        load_dotenv(override=False)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            self.model = None
            if genai is None:
                logger.warning("google-generativeai not installed. Skipping Gemini setup.")
            else:
                logger.warning("GEMINI_API_KEY not set. Gemini service disabled.")
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.system_prompt = (
            "You are a helpful college chatbot assistant. Keep responses concise,"
            " friendly, and informative."
        )

    def generate_response(self, question: str, context: str = "") -> dict:
        if not self.model:
            raise Exception("Gemini model not initialized")

        full_prompt = f"{self.system_prompt}\n\nContext: {context}\n\nStudent Question: {question}\n\nResponse:"
        response = self.model.generate_content(full_prompt)
        if getattr(response, "text", None):
            return {"answer": response.text.strip(), "confidence": 0.9, "source": "gemini"}
        raise Exception("Empty response from Gemini")


# Optional global instance
gemini_service = GeminiService()