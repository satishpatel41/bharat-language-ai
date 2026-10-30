"""Audio and video translation: transcribe, translate by segment, build subtitles."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import TypeVar

from app.errors import MediaProcessingError
from app.languages import get_language, is_supported, resolve_source
from app.providers.base import SpeechToText, Translator
from app.schemas import MediaTranslationResult, SegmentOut
from app.services.ffmpeg import extract_audio
from app.services.srt import format_srt

SEGMENT_BATCH_SIZE = 40


T = TypeVar("T")


def _chunks(items: Sequence[T], size: int) -> Iterator[Sequence[T]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


async def translate_audio(
    stt: SpeechToText,
    translator: Translator,
    audio_path: Path,
    target: str,
    source: str | None = "auto",
) -> MediaTranslationResult:
    target_lang = get_language(target)
    source_code = resolve_source(source)
    speech_code = get_language(source_code).whisper_code if source_code else None

    transcript = await stt.transcribe(audio_path, speech_code)
    segments = [seg for seg in transcript.segments if seg.text.strip()]
    if not segments:
        raise MediaProcessingError("No speech was detected in this file.")

    detected = transcript.language if is_supported(transcript.language) else None
    prompt_source = source_code or detected

    translated: list[str] = []
    for batch in _chunks(segments, SEGMENT_BATCH_SIZE):
        translated.extend(
            await translator.translate_batch(
                [seg.text.strip() for seg in batch], target_lang.code, prompt_source
            )
        )

    out_segments = [
        SegmentOut(start=seg.start, end=seg.end, text=seg.text.strip(), translated_text=text)
        for seg, text in zip(segments, translated, strict=True)
    ]
    return MediaTranslationResult(
        source_language=source_code or transcript.language,
        target_language=target_lang.code,
        transcript=" ".join(seg.text for seg in out_segments),
        translated_text=" ".join(seg.translated_text for seg in out_segments),
        segments=out_segments,
        srt=format_srt((seg.start, seg.end, seg.translated_text) for seg in out_segments),
    )


async def translate_video(
    stt: SpeechToText,
    translator: Translator,
    video_path: Path,
    target: str,
    source: str | None = "auto",
    ffmpeg_timeout: float = 300,
) -> MediaTranslationResult:
    # Validate languages before doing any expensive work.
    get_language(target)
    resolve_source(source)

    audio_path = video_path.parent / "audio.wav"
    await extract_audio(video_path, audio_path, timeout=ffmpeg_timeout)
    return await translate_audio(stt, translator, audio_path, target, source)
