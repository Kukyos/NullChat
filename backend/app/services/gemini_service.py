"""
Gemini AI service for generating intelligent responses
"""
import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Configure Gemini API with new direct key
        api_key = "AIzaSyCKFTwyEpJ7hSE9hqfTfL6kaYlGxnWM1k0"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        # System prompt for college chatbot
        self.system_prompt = """
You are a helpful college chatbot assistant. You answer questions about:
- Fee structures and payment deadlines (admission fees, hostel fees, etc.)
- Admission processes and requirements  
- Exam schedules and results
- Hostel facilities and rules
- Academic programs and courses
- Campus facilities and services
- Opening day schedules and events

Important: Answer naturally and concisely. If the question is in Hindi/Urdu mixed with English (like "kab 1st years ka opening day hai?"), respond in a similar mixed style (like "Opening day April 11th hai"). 

For specific dates and details you don't know, give placeholder examples like "April 11th" or say "exact date ke liye office se contact kariye".

Keep responses helpful and natural-sounding.
"""
    
    def generate_response(self, question: str, context: str = "") -> dict:
        """Generate response using Gemini AI"""
        if not self.model:
            raise Exception("Gemini model not initialized")
        
        # Prepare the prompt
        full_prompt = f"{self.system_prompt}\n\nContext: {context}\n\nStudent Question: {question}\n\nResponse:"
        
        # Generate response
        response = self.model.generate_content(full_prompt)
        
        if response.text:
            return {
                "answer": response.text.strip(),
                "confidence": 0.9,  # High confidence for Gemini responses
                "source": "gemini"
            }
        else:
            raise Exception("Empty response from Gemini")
    


# Global Gemini service instance
gemini_service = GeminiService()