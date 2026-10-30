from __future__ import annotations

import io
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.deps import get_stt, get_translator
from app.main import create_app
from tests.fakes import FakeSTT, FakeTranslator

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


@pytest.fixture
def translator() -> FakeTranslator:
    return FakeTranslator()


@pytest.fixture
def stt() -> FakeSTT:
    return FakeSTT()


@pytest.fixture
def client(translator: FakeTranslator, stt: FakeSTT) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_translator] = lambda: translator
    app.dependency_overrides[get_stt] = lambda: stt
    app.dependency_overrides[get_settings] = lambda: Settings(
        max_image_bytes=1024, max_audio_bytes=1024, max_video_bytes=1024
    )
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def png_file() -> io.BytesIO:
    return io.BytesIO(PNG_BYTES)
