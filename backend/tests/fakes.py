"""In-memory stand-ins for the translator and speech-to-text providers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from app.providers.base import ImageTranslation, Segment, TextTranslation, Transcript


class FakeTranslator:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    async def translate(self, text: str, target: str, source: str | None) -> TextTranslation:
        self.calls.append(("text", text, target, str(source)))
        return TextTranslation(source_language=source or "en", text=f"[{target}] {text}")

    async def translate_batch(
        self, texts: Sequence[str], target: str, source: str | None
    ) -> list[str]:
        self.calls.append(("batch", str(len(texts)), target, str(source)))
        return [f"[{target}] {text}" for text in texts]

    async def translate_image(self, image: bytes, media_type: str, target: str) -> ImageTranslation:
        self.calls.append(("image", media_type, target))
        return ImageTranslation(
            source_language="hi", extracted_text="नमस्ते", translated_text=f"[{target}] hello"
        )


class FakeSTT:
    def __init__(self, language: str = "hi", segments: list[Segment] | None = None) -> None:
        self.language = language
        self.segments = (
            segments
            if segments is not None
            else [Segment(0.0, 1.5, " नमस्ते "), Segment(1.5, 3.25, "आप कैसे हैं")]
        )
        self.requested_language: str | None = "unset"

    async def transcribe(self, audio_path: Path, language: str | None) -> Transcript:
        self.requested_language = language
        return Transcript(language=self.language, segments=list(self.segments))
