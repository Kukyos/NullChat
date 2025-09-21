
"""
Groq AI service for generating intelligent multilingual responses
"""

# Ensure .env is loaded before anything else
from dotenv import load_dotenv
import os
import sys
from getpass import getpass
# Try loading env from both backend/.env and backend/app/.env
_APP_DIR = os.path.dirname(__file__)
_BACKEND_DIR = os.path.abspath(os.path.join(_APP_DIR, '..'))
_BACKEND_ENV = os.path.join(_BACKEND_DIR, '.env')
_APP_ENV = os.path.join(_APP_DIR, '.env')
for _candidate in (_BACKEND_ENV, _APP_ENV):
    if os.path.exists(_candidate):
        load_dotenv(dotenv_path=_candidate, override=False)

import requests
import logging
from ..data.college_data import COLLEGE_INFO

logger = logging.getLogger(__name__)

def _is_interactive_tty() -> bool:
    """Return True if running in an interactive TTY session suitable for prompting."""
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except Exception:
        return False

def get_groq_api_key() -> str:
    """Resolve the Groq API key with safe, environment-first logic.

    Order:
    1) Environment variable `GROQ_API_KEY` (including values loaded from .env)
    2) If interactive TTY, prompt the user (hidden input)
    3) Otherwise, raise a helpful ValueError
    """
    # 1) Read from environment/.env
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key

    # 2) Only prompt if running interactively (avoids hangs in servers/Colab/CI)
    if _is_interactive_tty():
        print("GROQ_API_KEY is not set. Please paste your Groq API key. Input will be hidden.")
        entered = getpass("GROQ_API_KEY: ").strip()
        if entered:
            # Set for current process so subsequent uses work without re-prompting
            os.environ["GROQ_API_KEY"] = entered
            return entered

    # 3) Non-interactive: fail fast with guidance
    raise ValueError(
        "GROQ_API_KEY environment variable not set. Set it in your environment or backend/.env before starting the server. "
        "(Colab users: ensure the notebook writes the key to .env before starting the backend.)"
    )

class GroqService:
    def __init__(self):
        # Resolve API key (env/.env first; interactive prompt only when safe)
        self.api_key = get_groq_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # Fast Llama 3.1 8B model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_system_prompt(self, response_language: str) -> str:
        if response_language in ("hi", "mwr"):
            return f"""You are a helpful college chatbot assistant for State Institute of Technology. Always answer in Romanized Hindi (use English letters, not Devanagari script), even if the user asks in Marwari or Hindi. Do not use Hindi script. Do not use English except for names or technical terms.

COLLEGE INFORMATION:
{COLLEGE_INFO}

Instructions:
- Answer questions about college admissions, fees, hostel facilities, exam schedules, and campus information
- Use the college information provided above to give accurate, specific answers
- Keep responses concise but informative
- For specific dates you don't know, use examples from the college data or say 'exact date ke liye office se contact kariye'
- Always be helpful and student-friendly
"""
        else:
            return f"""You are a helpful college chatbot assistant for State Institute of Technology. Always answer in clear, simple English, regardless of the user's language. Keep your answers as short, direct, and easy to translate as possible. Avoid long explanations, repetition, or unnecessary details.

COLLEGE INFORMATION:
{COLLEGE_INFO}

Instructions:
- Answer questions about college admissions, fees, hostel facilities, exam schedules, and campus information
- Use the college information provided above to give accurate, specific answers
- Keep responses concise, direct, and easy to translate
- For specific dates you don't know, use examples from the college data or say 'please contact the office for the exact date'
- Always be helpful and student-friendly
"""
    
    def generate_response(self, question: str, response_language: str = "en", context: str = "") -> dict:
        """Generate response using Groq AI, with dynamic system prompt for Romanized Hindi/Marwari or English."""
        try:
            # First check if API key is properly set
            if not self.api_key or self.api_key == "YOUR_GROQ_API_KEY_HERE":
                return {
                    "answer": "Groq API key is not configured. Please add your API key to the service.",
                    "confidence": 0.1,
                    "source": "config-error"
                }
            system_prompt = self.get_system_prompt(response_language)
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            logger.info(f"Sending request to Groq API with model: {self.model} and response_language: {response_language}")
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                answer = data['choices'][0]['message']['content'].strip()
                return {
                    "answer": answer,
                    "confidence": 0.9,
                    "source": "groq-llama3"
                }
            else:
                error_details = response.text
                logger.error(f"Groq API error: {response.status_code}")
                logger.error(f"Response body: {error_details}")
                logger.error(f"Request payload: {payload}")
                # Return a fallback response instead of crashing
                return {
                    "answer": f"Sorry, I'm having trouble connecting to the AI service right now. API Error: {response.status_code}. Please try again later or contact support.",
                    "confidence": 0.1,
                    "source": "error-fallback"
                }
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise e

# Global Groq service instance
groq_service = GroqService()