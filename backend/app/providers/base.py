"""Provider interfaces. Services depend on these, never on a concrete vendor."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TextTranslation:
    source_language: str
    text: str


@dataclass(frozen=True, slots=True)
class ImageTranslation:
    source_language: str
    extracted_text: str
    translated_text: str


@dataclass(frozen=True, slots=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True, slots=True)
class Transcript:
    language: str
    segments: list[Segment]


class Translator(Protocol):
    async def translate(self, text: str, target: str, source: str | None) -> TextTranslation: ...

    async def translate_batch(
        self, texts: Sequence[str], target: str, source: str | None
    ) -> list[str]: ...

    async def translate_image(
        self, image: bytes, media_type: str, target: str
    ) -> ImageTranslation: ...


class SpeechToText(Protocol):
    async def transcribe(self, audio_path: Path, language: str | None) -> Transcript: ...
