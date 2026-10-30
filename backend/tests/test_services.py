from __future__ import annotations

from pathlib import Path

import pytest

from app.errors import (
    MediaProcessingError,
    TranscriptionUnavailableError,
    UnsupportedLanguageError,
    UnsupportedMediaError,
)
from app.providers.base import Segment
from app.services import image as image_service
from app.services import media as media_service
from app.services import text as text_service
from app.services.ffmpeg import build_extract_audio_args, extract_audio
from tests.conftest import PNG_BYTES
from tests.fakes import FakeSTT, FakeTranslator


async def test_translate_text_validates_and_normalises():
    translator = FakeTranslator()
    result = await text_service.translate_text(translator, "  Hello  ", "HI", "auto")
    assert result.target_language == "hi"
    assert result.translated_text == "[hi] Hello"
    assert translator.calls == [("text", "Hello", "hi", "None")]


async def test_translate_text_rejects_unknown_target():
    with pytest.raises(UnsupportedLanguageError):
        await text_service.translate_text(FakeTranslator(), "Hello", "klingon")


async def test_translate_text_rejects_unknown_source():
    with pytest.raises(UnsupportedLanguageError):
        await text_service.translate_text(FakeTranslator(), "Hello", "hi", "klingon")


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x89PNG\r\n\x1a\nxxxx", "image/png"),
        (b"\xff\xd8\xff\xe0xxxx", "image/jpeg"),
        (b"GIF89a....", "image/gif"),
        (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp"),
        (b"%PDF-1.7", None),
        (b"", None),
    ],
)
def test_detect_image_type(data, expected):
    assert image_service.detect_image_type(data) == expected


async def test_translate_image_uses_detected_type_not_client_claim():
    translator = FakeTranslator()
    result = await image_service.translate_image(translator, PNG_BYTES, "en")
    assert result.extracted_text == "नमस्ते"
    assert translator.calls == [("image", "image/png", "en")]


async def test_translate_image_rejects_non_image():
    with pytest.raises(UnsupportedMediaError):
        await image_service.translate_image(FakeTranslator(), b"not an image", "en")


async def test_translate_audio_builds_segments_and_srt(tmp_path: Path):
    stt = FakeSTT(language="hi")
    translator = FakeTranslator()
    result = await media_service.translate_audio(stt, translator, tmp_path / "a.wav", "en")
    assert result.source_language == "hi"
    assert [s.text for s in result.segments] == ["नमस्ते", "आप कैसे हैं"]
    assert result.translated_text == "[en] नमस्ते [en] आप कैसे हैं"
    assert "00:00:01,500 --> 00:00:03,250" in result.srt
    assert stt.requested_language is None
    # Detected supported language is passed to the translator as the source hint.
    assert translator.calls == [("batch", "2", "en", "hi")]


async def test_translate_audio_passes_speech_code_for_explicit_source(tmp_path: Path):
    stt = FakeSTT()
    await media_service.translate_audio(stt, FakeTranslator(), tmp_path / "a.wav", "en", "gu")
    assert stt.requested_language == "gu"


async def test_translate_audio_without_whisper_support_falls_back_to_auto(tmp_path: Path):
    stt = FakeSTT()
    # Bodo has no dedicated speech model, so the engine should auto-detect.
    await media_service.translate_audio(stt, FakeTranslator(), tmp_path / "a.wav", "en", "brx")
    assert stt.requested_language is None


async def test_translate_audio_ignores_blank_segments(tmp_path: Path):
    stt = FakeSTT(segments=[Segment(0, 1, "   "), Segment(1, 2, "hello")])
    result = await media_service.translate_audio(stt, FakeTranslator(), tmp_path / "a.wav", "hi")
    assert len(result.segments) == 1


async def test_translate_audio_with_no_speech_errors(tmp_path: Path):
    stt = FakeSTT(segments=[])
    with pytest.raises(MediaProcessingError):
        await media_service.translate_audio(stt, FakeTranslator(), tmp_path / "a.wav", "hi")


async def test_translate_audio_batches_long_transcripts(tmp_path: Path):
    count = media_service.SEGMENT_BATCH_SIZE + 5
    stt = FakeSTT(segments=[Segment(i, i + 1, f"line {i}") for i in range(count)])
    translator = FakeTranslator()
    result = await media_service.translate_audio(stt, translator, tmp_path / "a.wav", "hi")
    assert len(result.segments) == count
    assert [call[1] for call in translator.calls] == [str(media_service.SEGMENT_BATCH_SIZE), "5"]


async def test_translate_video_validates_languages_before_extracting(tmp_path: Path):
    with pytest.raises(UnsupportedLanguageError):
        await media_service.translate_video(
            FakeSTT(), FakeTranslator(), tmp_path / "missing.mp4", "nope"
        )


def test_ffmpeg_args_extract_mono_16khz_wav():
    args = build_extract_audio_args(Path("in.mp4"), Path("out.wav"))
    assert args[0] == "ffmpeg"
    assert args[args.index("-ar") + 1] == "16000"
    assert args[args.index("-ac") + 1] == "1"
    assert args[args.index("-i") + 1] == "in.mp4"
    assert args[-1] == "out.wav"


async def test_extract_audio_reports_unreadable_video(tmp_path: Path):
    import shutil

    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"this is not a video")
    if shutil.which("ffmpeg") is None:
        with pytest.raises(TranscriptionUnavailableError):
            await extract_audio(bad, tmp_path / "out.wav")
    else:
        with pytest.raises(MediaProcessingError):
            await extract_audio(bad, tmp_path / "out.wav")
