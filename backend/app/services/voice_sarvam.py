<<<<<<< Updated upstream
"""Sarvam AI voice service placeholder.

This module provides three endpoints:
- POST /voice/stt : speech -> text (placeholder)
- POST /voice/tts : text -> audio (placeholder)
- POST /voice/chat : combined pipeline (audio in -> answer text + synthesized audio)

Replace the placeholder SARVAM_* endpoints and logic with real Sarvam API calls.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse, JSONResponse
=======
"""Sarvam AI voice service (REAL ONLY).

Removed all placeholder / mock transcript / silent audio generation.
All endpoints require a valid Sarvam API key.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
>>>>>>> Stashed changes
from sqlalchemy.orm import Session
from ..database import get_db
from .chat_pipeline import process_question
from .translation import translator_service
import base64
import os
import io
import uuid
import logging
<<<<<<< Updated upstream

logger = logging.getLogger(__name__)
=======
import json
from typing import Optional, Tuple
import subprocess
import shutil

try:
    import httpx  # lightweight async HTTP client
except ImportError:  # guidance if missing
    httpx = None  # Will raise informative error when real mode requested

logger = logging.getLogger(__name__)
BUILD_TAG = "voice-real-only-v1"  # increment if changing voice pipeline semantics
logger.info(f"[voice_init] Loading voice module build={BUILD_TAG} real_only={True}")
>>>>>>> Stashed changes

router = APIRouter(prefix="/voice", tags=["voice"])

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
<<<<<<< Updated upstream
# Placeholder endpoints (update with real Sarvam endpoints)
SARVAM_STT_ENDPOINT = os.getenv("SARVAM_STT_ENDPOINT", "https://api.sarvam.ai/v1/audio/transcribe")
SARVAM_TTS_ENDPOINT = os.getenv("SARVAM_TTS_ENDPOINT", "https://api.sarvam.ai/v1/audio/synthesize")
=======
SARVAM_STT_ENDPOINT = os.getenv("SARVAM_STT_ENDPOINT", "https://api.sarvam.ai/v1/audio/transcribe")
SARVAM_TTS_ENDPOINT = os.getenv("SARVAM_TTS_ENDPOINT", "https://api.sarvam.ai/v1/audio/synthesize")
SARVAM_REAL_MODE = True  # Force real mode
SARVAM_TTS_VOICE = os.getenv("SARVAM_TTS_VOICE", "default")
SARVAM_TTS_FORMAT = os.getenv("SARVAM_TTS_FORMAT", "wav")
SARVAM_TIMEOUT_SEC = float(os.getenv("SARVAM_TIMEOUT", "30"))
>>>>>>> Stashed changes


def _require_key():
    if not SARVAM_API_KEY:
        raise HTTPException(status_code=500, detail="Sarvam API key not configured (set SARVAM_API_KEY)")
<<<<<<< Updated upstream

@router.post("/stt")
async def stt(file: UploadFile = File(...)):
    """Convert uploaded audio to text (placeholder implementation)."""
    _require_key()
    # For now just return a dummy transcript; replace with real HTTP request.
    raw = await file.read()
    size_kb = len(raw) / 1024
    logger.info(f"[Sarvam STT placeholder] Received {size_kb:.1f} KB audio; returning dummy transcript")
    return {"transcript": "(transcript placeholder)"}

@router.post("/tts")
async def tts(text: str = Body(..., embed=True)):
    """Convert text to audio (placeholder). Returns base64 mp3 bytes."""
    _require_key()
    fake_audio = b"FAKEAUDIOBYTES"  # Replace with real Sarvam TTS response bytes
    b64 = base64.b64encode(fake_audio).decode()
    return {"audio_base64": b64, "length": len(fake_audio)}
=======
    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx not installed. Run 'pip install httpx'")

async def _real_stt(audio_bytes: bytes, content_type: str | None) -> str:
    """Call real Sarvam STT endpoint. Returns transcript string.

    Expected Sarvam API contract (adjust fields as per official docs):
    - POST multipart/form-data with field 'file'
    - Auth via Authorization: Bearer <API_KEY>
    - JSON response containing 'text' or 'transcript'
    """
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
    }
    if httpx is None:
        raise RuntimeError("httpx not available")
    async with httpx.AsyncClient(timeout=SARVAM_TIMEOUT_SEC) as client:
        files = {"file": ("audio", audio_bytes, content_type or "application/octet-stream")}
        try:
            resp = await client.post(SARVAM_STT_ENDPOINT, headers=headers, files=files)
        except httpx.RequestError as e:
            logger.error(f"Sarvam STT network error: {e}")
            raise HTTPException(status_code=502, detail="Sarvam STT network error")
        if resp.status_code >= 400:
            logger.error(f"Sarvam STT error {resp.status_code}: {resp.text[:300]}")
            raise HTTPException(status_code=502, detail=f"Sarvam STT failed ({resp.status_code})")
        data = resp.json()
        transcript = data.get("text") or data.get("transcript")
        if not transcript:
            logger.warning(f"Sarvam STT response missing transcript field: {data}")
            raise HTTPException(status_code=502, detail="Sarvam STT returned no transcript")
        logger.info("Sarvam STT success")
        return transcript

async def _real_tts(text: str) -> Tuple[str, str]:
    """Call real Sarvam TTS endpoint. Returns (audio_base64, format)."""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice": SARVAM_TTS_VOICE,
        "format": SARVAM_TTS_FORMAT,
    }
    if httpx is None:
        raise RuntimeError("httpx not available")
    async with httpx.AsyncClient(timeout=SARVAM_TIMEOUT_SEC) as client:
        try:
            resp = await client.post(SARVAM_TTS_ENDPOINT, headers=headers, json=payload)
        except httpx.RequestError as e:
            logger.error(f"Sarvam TTS network error: {e}")
            raise HTTPException(status_code=502, detail="Sarvam TTS network error")
        if resp.status_code >= 400:
            logger.error(f"Sarvam TTS error {resp.status_code}: {resp.text[:300]}")
            raise HTTPException(status_code=502, detail=f"Sarvam TTS failed ({resp.status_code})")
        data = resp.json()
        audio_b64 = data.get("audio_base64") or data.get("audio")
        fmt = data.get("format") or SARVAM_TTS_FORMAT
        if not audio_b64:
            logger.warning(f"Sarvam TTS response missing audio field: {data}")
            raise HTTPException(status_code=502, detail="Sarvam TTS returned no audio")
        logger.info("Sarvam TTS success")
        return audio_b64, fmt

def _sniff_audio(raw: bytes) -> dict:
    """Very small helper to inspect uploaded audio and return pseudo metadata.
    Supports quick WAV/Riff header detection; otherwise labels as 'unknown'."""
    meta = {"format": "unknown", "bytes": len(raw)}
    if len(raw) >= 12 and raw[:4] == b'RIFF' and raw[8:12] == b'WAVE':
        meta["format"] = "wav"
    return meta

def _prepare_audio_for_stt(raw: bytes, content_type: str | None) -> tuple[bytes, str]:
    """If the browser sent webm/ogg (likely opus), convert to wav pcm16 using ffmpeg if available.
    Returns (bytes, new_content_type). If conversion fails, falls back to original bytes.
    """
    ct = (content_type or '').lower()
    if 'webm' not in ct and 'ogg' not in ct:
        return raw, content_type or 'application/octet-stream'
    if not shutil.which('ffmpeg'):
        logger.warning('ffmpeg not found on PATH; sending original webm/ogg bytes to Sarvam (may fail).')
        return raw, content_type or 'application/octet-stream'
    try:
        proc = subprocess.run(
            ['ffmpeg', '-f', 'webm', '-i', 'pipe:0', '-f', 'wav', '-acodec', 'pcm16le', '-ac', '1', '-ar', '16000', 'pipe:1'],
            input=raw,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        wav_bytes = proc.stdout
        if not wav_bytes.startswith(b'RIFF'):
            logger.warning('ffmpeg produced output without RIFF header; falling back to original bytes.')
            return raw, content_type or 'application/octet-stream'
        logger.info(f'Converted webm/ogg -> wav ({len(raw)} -> {len(wav_bytes)} bytes)')
        return wav_bytes, 'audio/wav'
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg conversion failed: {e.stderr[:200].decode(errors="ignore")}')
        return raw, content_type or 'application/octet-stream'


@router.post("/stt")
async def stt(file: UploadFile = File(...)):
    """Speech to text via Sarvam (real only)."""
    _require_key()
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty audio upload")
    prepared_bytes, prepared_type = _prepare_audio_for_stt(raw, file.content_type)
    meta = _sniff_audio(prepared_bytes)
    transcript = await _real_stt(prepared_bytes, prepared_type)
    logger.info(f"Voice STT transcript len={len(transcript)} preview='{transcript[:60]}'")
    return {"transcript": transcript, "provider": "sarvam", "meta": meta}


@router.post("/tts")
async def tts(text: str = Body(..., embed=True)):
    """Text to speech via Sarvam (real only)."""
    _require_key()
    audio_b64, fmt = await _real_tts(text)
    return {"audio_base64": audio_b64, "format": fmt, "provider": "sarvam"}
>>>>>>> Stashed changes

@router.post("/chat")
async def voice_chat(
    file: UploadFile = File(...),
    language: str | None = None,
    session_id: str | None = None,
    db: Session = Depends(get_db),
):
<<<<<<< Updated upstream
    """End-to-end voice chat:
    1. STT via Sarvam (placeholder)
    2. Process question via existing Groq pipeline
    3. TTS answer via Sarvam (placeholder audio)
    Returns transcript, answer text, and base64 audio.
    """
=======
    """End-to-end voice chat (real only)."""
>>>>>>> Stashed changes
    _require_key()
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")
<<<<<<< Updated upstream

    # Placeholder STT
    transcript = "(transcript placeholder from audio)"
    user_lang = language or "auto"

    # Use unified pipeline (so voice & text share logic)
=======
    prepared_bytes, prepared_type = _prepare_audio_for_stt(audio_bytes, file.content_type)
    transcript = await _real_stt(prepared_bytes, prepared_type)
    logger.info(f"Voice CHAT transcript len={len(transcript)} preview='{transcript[:60]}'")
    user_lang = language or "auto"
>>>>>>> Stashed changes
    pipeline = process_question(
        question=transcript,
        incoming_language=user_lang,
        session_id=session_id,
        db=db,
    )
    answer_text = pipeline["answer"]
    confidence = pipeline["confidence"]
    user_lang = pipeline["language_detected"]
    conv_id = pipeline["conversation_id"]
<<<<<<< Updated upstream

    # Placeholder TTS
    fake_audio = b"FAKEAUDIOANSWER"  # Replace with Sarvam TTS bytes
    audio_b64 = base64.b64encode(fake_audio).decode()

=======
    audio_b64, audio_fmt = await _real_tts(answer_text)
>>>>>>> Stashed changes
    return {
        "transcript": transcript,
        "answer": answer_text,
        "confidence": confidence,
        "language_detected": user_lang,
        "conversation_id": conv_id,
        "audio_base64": audio_b64,
<<<<<<< Updated upstream
=======
        "audio_format": audio_fmt,
        "stt_provider": "sarvam",
        "tts_provider": "sarvam",
        "mode": "real",
    }

@router.get("/status")
async def voice_status():
    """Lightweight status for debugging voice pipeline configuration."""
    return {
        "build": BUILD_TAG,
        "requires_ffmpeg_for_webm": True,
        "ffmpeg_available": shutil.which('ffmpeg') is not None,
        "stt_endpoint": SARVAM_STT_ENDPOINT,
        "tts_endpoint": SARVAM_TTS_ENDPOINT,
        "voice": SARVAM_TTS_VOICE,
        "format": SARVAM_TTS_FORMAT,
        "timeout_sec": SARVAM_TIMEOUT_SEC,
>>>>>>> Stashed changes
    }
