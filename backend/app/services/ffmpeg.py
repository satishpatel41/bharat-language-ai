"""Audio extraction from video via the ffmpeg binary."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app.errors import MediaProcessingError, TranscriptionUnavailableError


def build_extract_audio_args(video: Path, output: Path) -> list[str]:
    """Mono 16 kHz WAV, the format speech models expect."""
    return [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-i",
        str(video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        str(output),
    ]


async def extract_audio(video: Path, output: Path, timeout: float = 300) -> None:
    args = build_extract_audio_args(video, output)
    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise TranscriptionUnavailableError("ffmpeg is not installed on this server.") from exc

    try:
        await asyncio.wait_for(process.wait(), timeout=timeout)
    except TimeoutError as exc:
        process.kill()
        await process.wait()
        raise MediaProcessingError("Reading the video took too long.") from exc

    if process.returncode != 0 or not output.exists():
        raise MediaProcessingError("Could not read an audio track from this video.")
