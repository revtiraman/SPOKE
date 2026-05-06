"""Agent 1 — Transcriber: converts video/audio to clean structured text."""

from __future__ import annotations
import os
import time
import tempfile
from pathlib import Path

from loguru import logger

from core.models import TranscriptResult
from core.config import settings


class TranscriberAgent:
    """Transcribes video or audio files to text using Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        self._ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        import shutil
        return shutil.which("ffmpeg") is not None

    def _load_model(self):
        if self._model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model: {self.model_size}")
                self._model = whisper.load_model(self.model_size)
                logger.success("Whisper model loaded")
            except ImportError:
                logger.warning("Whisper not available — using HuggingFace API fallback")
                self._model = "hf_fallback"
        return self._model

    async def transcribe(self, video_path: str) -> TranscriptResult:
        """Transcribe a video or audio file to text."""
        t0 = time.perf_counter()
        path = Path(video_path)

        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        logger.info(f"Transcribing: {path.name} ({path.stat().st_size / 1024:.1f} KB)")

        # Extract audio if video format
        audio_path = video_path
        if path.suffix.lower() in {".mp4", ".mov", ".webm", ".avi", ".mkv"}:
            audio_path = await self._extract_audio(video_path)

        model = self._load_model()

        if model == "hf_fallback":
            result = await self._transcribe_hf(audio_path)
        else:
            result = self._transcribe_whisper(model, audio_path)

        elapsed = time.perf_counter() - t0
        logger.success(f"Transcription complete in {elapsed:.1f}s — {result.word_count} words")
        return result

    def _transcribe_whisper(self, model, audio_path: str) -> TranscriptResult:
        """Run local Whisper transcription."""
        import whisper
        result = model.transcribe(audio_path, language=None, task="transcribe")
        text = result["text"].strip()
        language = result.get("language", "en")
        segments = result.get("segments", [])
        duration = segments[-1]["end"] if segments else 0.0

        flagged = [
            s["text"].strip()
            for s in segments
            if s.get("avg_logprob", 0) < -1.0
        ]

        cleaned = self._clean_text(text)
        confidence = max(0.0, min(1.0, 1.0 + (sum(s.get("avg_logprob", -0.5) for s in segments) / max(len(segments), 1))))

        return TranscriptResult(
            raw_text=text,
            cleaned_text=cleaned,
            duration_seconds=duration,
            confidence_score=confidence,
            language_detected=language,
            word_count=len(cleaned.split()),
            flagged_segments=flagged[:3],
        )

    async def _transcribe_hf(self, audio_path: str) -> TranscriptResult:
        """Fallback: use HuggingFace Inference API for transcription.

        Only works when HF_API_TOKEN is a real HuggingFace token (hf_...).
        For other providers (Cerebras, Gemini, Groq) the token is not valid
        for the HF Inference API, so we fall back gracefully to an empty
        transcript rather than crashing the pipeline.
        """
        import httpx

        token = settings.whisper_token
        # HF Inference API only accepts hf_* tokens
        if not token:
            logger.warning(
                "Whisper HF API skipped — no HuggingFace token available. "
                "Set HF_WHISPER_TOKEN=hf_... in .env to enable video transcription."
            )
            return self._empty_transcript()

        file_size = Path(audio_path).stat().st_size
        if file_size == 0:
            logger.warning("Audio file is empty (0 bytes) — skipping HF Whisper call.")
            return self._empty_transcript()

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3",
                    content=audio_bytes,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.warning(f"HF Whisper API failed ({e}) — returning empty transcript.")
            return self._empty_transcript()

        text = data.get("text", "")
        cleaned = self._clean_text(text)
        return TranscriptResult(
            raw_text=text,
            cleaned_text=cleaned,
            confidence_score=0.85,
            language_detected="en",
            word_count=len(cleaned.split()),
        )

    def _empty_transcript(self) -> TranscriptResult:
        """Return a placeholder transcript when audio cannot be transcribed."""
        return TranscriptResult(
            raw_text="",
            cleaned_text="",
            duration_seconds=0.0,
            confidence_score=0.0,
            language_detected="en",
            word_count=0,
            flagged_segments=[],
        )

    async def _extract_audio(self, video_path: str) -> str:
        """Extract audio track from video file using ffmpeg."""
        if not self._ffmpeg_available:
            logger.warning("ffmpeg not found — attempting to use video file directly")
            return video_path

        import asyncio
        out_path = video_path.replace(Path(video_path).suffix, ".wav")
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", out_path, "-y", "-loglevel", "error",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"ffmpeg error: {stderr.decode()}")
            return video_path
        return out_path

    def _clean_text(self, text: str) -> str:
        """Clean and normalize transcript text."""
        import re
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"([.!?])\s+([a-z])", lambda m: m.group(1) + " " + m.group(2).upper(), text)
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        return text

    async def transcribe_demo(self, sample_text: str | None = None) -> TranscriptResult:
        """Return a realistic demo transcription without touching any file."""
        text = sample_text or (
            "Hi, I run a small e-commerce business. Every day I get about 10 to 15 order emails. "
            "I manually open each one, read the customer name, product, quantity, and price, "
            "then I open Google Sheets and type it all in row by row. "
            "It takes me about 2 hours every single day. "
            "It's the most boring and repetitive part of my job and I keep making typos."
        )
        return TranscriptResult(
            raw_text=text,
            cleaned_text=text,
            duration_seconds=47.3,
            confidence_score=0.96,
            language_detected="en",
            word_count=len(text.split()),
            flagged_segments=[],
        )
