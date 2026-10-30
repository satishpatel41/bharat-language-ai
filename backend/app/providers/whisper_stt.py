"""Local speech recognition using faster-whisper (install with the `audio` extra)."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Any

from app.errors import TranscriptionUnavailableError
from app.providers.base import Segment, Transcript


class FasterWhisperSTT:
    def __init__(
        self, model_size: str = "small", device: str = "auto", compute_type: str = "int8"
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._model: Any = None
        self._lock = threading.Lock()

    def _load(self) -> Any:
        with self._lock:
            if self._model is None:
                try:
                    from faster_whisper import WhisperModel
                except ImportError as exc:
                    raise TranscriptionUnavailableError(
                        "Speech recognition is not installed on this server. "
                        "Install it with: pip install '.[audio]'"
                    ) from exc
                self._model = WhisperModel(
                    self._model_size, device=self._device, compute_type=self._compute_type
                )
            return self._model

    def _transcribe_sync(self, audio_path: Path, language: str | None) -> Transcript:
        model = self._load()
        segments, info = model.transcribe(str(audio_path), language=language, vad_filter=True)
        return Transcript(
            language=info.language,
            segments=[Segment(start=s.start, end=s.end, text=s.text) for s in segments],
        )

    async def transcribe(self, audio_path: Path, language: str | None) -> Transcript:
        return await asyncio.to_thread(self._transcribe_sync, audio_path, language)
