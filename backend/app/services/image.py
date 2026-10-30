from __future__ import annotations

from app.errors import UnsupportedMediaError
from app.languages import get_language
from app.providers.base import Translator
from app.schemas import ImageTranslationResult


def detect_image_type(data: bytes) -> str | None:
    """Identify the image type from its magic bytes rather than trusting the client."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


async def translate_image(
    translator: Translator, data: bytes, target: str
) -> ImageTranslationResult:
    target_lang = get_language(target)
    media_type = detect_image_type(data)
    if media_type is None:
        raise UnsupportedMediaError("Unsupported image. Upload a PNG, JPEG, GIF or WebP file.")
    result = await translator.translate_image(data, media_type, target_lang.code)
    return ImageTranslationResult(
        source_language=result.source_language,
        target_language=target_lang.code,
        extracted_text=result.extracted_text,
        translated_text=result.translated_text,
    )
