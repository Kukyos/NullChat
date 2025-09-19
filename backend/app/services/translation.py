"""
Translation service using Google Translate
"""
from googletrans import Translator, LANGUAGES
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import time

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def _detect_with_timeout(self, text: str, timeout: int = 5) -> str:
        """Detect language with timeout"""
        def _detect():
            return self.translator.detect(text).lang
        
        future = self.executor.submit(_detect)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            logger.warning(f"Language detection timed out after {timeout}s")
            return "en"
        
    def detect_language(self, text: str) -> str:
        """Detect the language of input text with timeout"""
        try:
            return self._detect_with_timeout(text, timeout=5)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"  # default to English
    
    def _translate_with_timeout(self, text: str, src: str, dest: str, timeout: int = 8) -> str:
        """Translate with timeout"""
        def _translate():
            return self.translator.translate(text, src=src, dest=dest).text
        
        future = self.executor.submit(_translate)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            logger.warning(f"Translation timed out after {timeout}s")
            return text
    
    def translate_to_english(self, text: str, source_lang: str = None) -> str:
        """Translate text to English with timeout"""
        try:
            if source_lang is None:
                source_lang = self.detect_language(text)
            
            if source_lang == "en":
                return text
                
            return self._translate_with_timeout(text, src=source_lang, dest="en", timeout=8)
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate text from English to target language with timeout. For Hindi/Marwari, return Romanized (Latin script)."""
        try:
            if target_lang == "en":
                return text
            # For Hindi and Marwari, return Romanized (Latin script)
            if target_lang in ("hi", "mwr"):
                # Googletrans transliteration only works for Hindi
                translated = self.translator.translate(text, src="en", dest="hi")
                # Use .pronunciation for Romanized output if available
                romanized = getattr(translated, "pronunciation", None)
                if romanized:
                    return romanized
                else:
                    return translated.text  # fallback to native script
            # All other languages: normal translation
            return self._translate_with_timeout(text, src="en", dest=target_lang, timeout=8)
        except Exception as e:
            logger.error(f"Translation from English failed: {e}")
            return text
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages"""
        return LANGUAGES

# Global translator instance
translator_service = TranslationService()