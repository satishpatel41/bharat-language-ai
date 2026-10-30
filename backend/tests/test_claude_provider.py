from __future__ import annotations

from types import SimpleNamespace

import anthropic
import httpx
import pytest

from app.errors import TranslationError
from app.providers.claude import ClaudeTranslator, extract_json


class FakeMessages:
    def __init__(self, reply: str | Exception) -> None:
        self.reply = reply
        self.kwargs: dict = {}

    async def create(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.reply, Exception):
            raise self.reply
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.reply)])


def make(reply: str | Exception) -> tuple[ClaudeTranslator, FakeMessages]:
    messages = FakeMessages(reply)
    client = SimpleNamespace(messages=messages)
    return ClaudeTranslator(client, "test-model"), messages


def test_extract_json_handles_code_fences_and_prose():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}


@pytest.mark.parametrize("raw", ["no json here", "{broken", "[1, 2]", "}{"])
def test_extract_json_rejects_bad_replies(raw):
    with pytest.raises(TranslationError):
        extract_json(raw)


async def test_translate_returns_detected_source():
    translator, messages = make('{"source_language": " EN ", "translation": "નમસ્તે"}')
    result = await translator.translate("Hello", "gu", None)
    assert result.source_language == "en"
    assert result.text == "નમસ્તે"
    assert messages.kwargs["model"] == "test-model"
    prompt = messages.kwargs["messages"][0]["content"]
    assert "Gujarati" in prompt
    assert "Detect the source language" in prompt


async def test_translate_uses_explicit_source_when_model_omits_it():
    translator, _ = make('{"translation": "hi"}')
    result = await translator.translate("x", "hi", "mr")
    assert result.source_language == "mr"


async def test_translate_missing_translation_is_an_error():
    translator, _ = make('{"source_language": "en"}')
    with pytest.raises(TranslationError):
        await translator.translate("x", "hi", None)


async def test_translate_batch_preserves_order_and_count():
    translator, messages = make('{"translations": ["a", "b"]}')
    assert await translator.translate_batch(["1", "2"], "ta", "en") == ["a", "b"]
    assert "exactly 2 strings" in messages.kwargs["messages"][0]["content"]


async def test_translate_batch_rejects_count_mismatch():
    translator, _ = make('{"translations": ["only one"]}')
    with pytest.raises(TranslationError):
        await translator.translate_batch(["1", "2"], "ta", None)


async def test_translate_batch_empty_makes_no_call():
    translator, messages = make("unused")
    assert await translator.translate_batch([], "ta", None) == []
    assert messages.kwargs == {}


async def test_translate_image_sends_base64_image_block():
    translator, messages = make(
        '{"source_language": "hi", "extracted_text": "नमस्ते", "translation": "Hello"}'
    )
    result = await translator.translate_image(b"\x89PNG", "image/png", "en")
    assert result.extracted_text == "नमस्ते"
    assert result.translated_text == "Hello"
    blocks = messages.kwargs["messages"][0]["content"]
    assert blocks[0]["type"] == "image"
    assert blocks[0]["source"]["media_type"] == "image/png"
    assert blocks[0]["source"]["type"] == "base64"


async def test_api_failure_becomes_translation_error():
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    translator, _ = make(anthropic.APIConnectionError(request=request))
    with pytest.raises(TranslationError):
        await translator.translate("x", "hi", None)


async def test_empty_model_reply_is_an_error():
    translator, _ = make("   ")
    with pytest.raises(TranslationError):
        await translator.translate("x", "hi", None)
