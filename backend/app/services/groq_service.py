
"""
Groq AI service for generating intelligent multilingual responses
"""

# Ensure .env is loaded before anything else
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

import requests
import logging
from ..data.college_data import COLLEGE_INFO

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        # Groq API configuration - API key is now loaded from environment variable or user input
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            try:
                # Prompt for API key if not found
                print("GROQ_API_KEY environment variable not set. Please enter your Groq API key:")
                self.api_key = input("Groq API Key: ").strip()
            except Exception:
                raise ValueError("GROQ_API_KEY environment variable not set and user input failed. Please set it in your environment or .env file.")
            if not self.api_key:
                raise ValueError("No Groq API key provided. Please set GROQ_API_KEY in your environment, .env file, or enter it when prompted.")
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
            logger.info(f"API Key prefix: {self.api_key[:10]}...")
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