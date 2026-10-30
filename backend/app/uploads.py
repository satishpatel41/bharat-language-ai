"""Bounded handling of uploaded files."""

from __future__ import annotations

import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import UploadFile

from app.errors import PayloadTooLargeError, UnsupportedMediaError

CHUNK_SIZE = 1024 * 1024

AUDIO_SUFFIXES = frozenset({".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".webm"})
VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".mkv", ".webm", ".avi"})


def _too_large(max_bytes: int) -> PayloadTooLargeError:
    return PayloadTooLargeError(f"File is larger than the {max_bytes} byte limit.")


async def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    buffer = bytearray()
    while chunk := await file.read(CHUNK_SIZE):
        buffer.extend(chunk)
        if len(buffer) > max_bytes:
            raise _too_large(max_bytes)
    return bytes(buffer)


@asynccontextmanager
async def spooled_upload(
    file: UploadFile, max_bytes: int, allowed_suffixes: frozenset[str]
) -> AsyncIterator[Path]:
    """Stream an upload to a temporary file that is deleted when the block exits."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed_suffixes:
        allowed = ", ".join(sorted(allowed_suffixes))
        raise UnsupportedMediaError(f"Unsupported file type. Allowed: {allowed}.")

    with tempfile.TemporaryDirectory(prefix="bharat-") as tmp:
        path = Path(tmp) / f"upload{suffix}"
        written = 0
        with path.open("wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                written += len(chunk)
                if written > max_bytes:
                    raise _too_large(max_bytes)
                out.write(chunk)
        yield path
