from __future__ import annotations

from functools import lru_cache

import anthropic

from app.config import get_settings
from app.errors import ConfigurationError
from app.providers.base import SpeechToText, Translator
from app.providers.claude import ClaudeTranslator
from app.providers.whisper_stt import FasterWhisperSTT


@lru_cache
def get_translator() -> Translator:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise ConfigurationError("ANTHROPIC_API_KEY is not configured on the server.")
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return ClaudeTranslator(client, settings.claude_model)


@lru_cache
def get_stt() -> SpeechToText:
    return FasterWhisperSTT(get_settings().whisper_model)
