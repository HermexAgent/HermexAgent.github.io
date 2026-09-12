"""
HermexAgent Voice Hub - Faster-Whisper Local STT & Edge-TTS Engine with Dynamic Quality Upgrades
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List

logger = logging.getLogger("HermexAgent.VoiceHub")

WHISPER_CATALOG = [
    {
        "id": "tiny",
        "name": "⚡️ Whisper Tiny",
        "size": "75 MB",
        "accuracy": "Low (Fastest)",
        "ram": "1 GB",
        "fa_quality": "⭐⭐"
    },
    {
        "id": "base",
        "name": "🔹 Whisper Base",
        "size": "145 MB",
        "accuracy": "Good (Lightweight)",
        "ram": "2 GB",
        "fa_quality": "⭐⭐⭐"
    },
    {
        "id": "small",
        "name": "⚖️ Whisper Small (Default)",
        "size": "480 MB",
        "accuracy": "High (Balanced)",
        "ram": "4 GB",
        "fa_quality": "⭐⭐⭐⭐"
    },
    {
        "id": "medium",
        "name": "🚀 Whisper Medium",
        "size": "1.5 GB",
        "accuracy": "Very High",
        "ram": "8 GB",
        "fa_quality": "⭐⭐⭐⭐⭐"
    },
    {
        "id": "large-v3-turbo",
        "name": "👑 Whisper Large-v3-Turbo",
        "size": "1.6 GB",
        "accuracy": "Maximum Precision (Best for Persian)",
        "ram": "8 GB",
        "fa_quality": "⭐⭐⭐⭐⭐"
    }
]

TTS_VOICES = [
    {"id": "fa-IR-DilaraNeural", "name": "🇮🇷 Dilara (Persian Female - Default)"},
    {"id": "fa-IR-FaridNeural", "name": "🇮🇷 Farid (Persian Male)"},
    {"id": "en-US-JennyNeural", "name": "🇺🇸 Jenny (English Female)"},
    {"id": "en-US-GuyNeural", "name": "🇺🇸 Guy (English Male)"}
]

class VoiceHub:
    def __init__(self, model_size: str = "small", device: str = "auto", tts_voice: str = "fa-IR-DilaraNeural"):
        self.model_size = model_size
        self.device = device
        self.tts_voice = tts_voice
        self._model = None

    def get_catalog(self) -> List[Dict[str, Any]]:
        return WHISPER_CATALOG

    def set_model_size(self, new_size: str):
        """Switch active Whisper model size."""
        if self.model_size != new_size:
            logger.info(f"Switching Whisper model from {self.model_size} to {new_size}")
            self.model_size = new_size
            self._model = None  # Force reload on next transcription

    def set_tts_voice(self, voice_id: str):
        self.tts_voice = voice_id

    def _load_whisper_if_needed(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                compute_type = "float16" if self.device == "cuda" else "int8"
                logger.info(f"Loading Faster-Whisper model ({self.model_size})...")
                self._model = WhisperModel(self.model_size, device=self.device, compute_type=compute_type)
            except Exception as e:
                logger.error(f"Failed to load WhisperModel: {e}")
                raise

    async def transcribe(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """Convert local audio/voice file to text with metadata."""
        try:
            def _run():
                self._load_whisper_if_needed()
                assert self._model is not None
                segments, info = self._model.transcribe(audio_path, beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip()
                return {
                    "text": text,
                    "language": info.language,
                    "probability": info.language_probability,
                    "duration": info.duration,
                    "model_used": self.model_size
                }
            
            return await asyncio.to_thread(_run)
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    async def synthesize(self, text: str, output_path: str, voice: Optional[str] = None) -> Optional[str]:
        """Convert text to speech audio file using edge-tts."""
        try:
            import edge_tts
            selected_voice = voice or self.tts_voice
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
