from __future__ import annotations

from app.languages import get_language, resolve_source
from app.providers.base import Translator
from app.schemas import TranslationResult


async def translate_text(
    translator: Translator, text: str, target: str, source: str | None = "auto"
) -> TranslationResult:
    target_lang = get_language(target)
    source_code = resolve_source(source)
    result = await translator.translate(text.strip(), target_lang.code, source_code)
    return TranslationResult(
        source_language=result.source_language,
        target_language=target_lang.code,
        original_text=text,
        translated_text=result.text,
    )
