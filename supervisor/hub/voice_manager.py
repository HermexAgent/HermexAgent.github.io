"""
HermesX Voice Hub - Faster-Whisper Local STT & Edge-TTS Engine
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("HermesX.VoiceHub")

class VoiceHub:
    def __init__(self, model_size: str = "small", device: str = "auto"):
        self.model_size = model_size
        self.device = device
        self._model = None

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

    async def transcribe(self, audio_path: str) -> Optional[str]:
        """Convert local audio/voice file to text."""
        try:
            self._load_whisper_if_needed()
            segments, info = self._model.transcribe(audio_path, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()
            return text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    async def synthesize(self, text: str, output_path: str, voice: str = "fa-IR-DilaraNeural"):
        """Convert text to speech audio file using edge-tts."""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
