"""SubRip (.srt) subtitle formatting."""

from __future__ import annotations

from collections.abc import Iterable


def format_timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rest = divmod(total_ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def format_srt(cues: Iterable[tuple[float, float, str]]) -> str:
    blocks = [
        f"{index}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{text.strip()}\n"
        for index, (start, end, text) in enumerate(cues, start=1)
    ]
    return "\n".join(blocks)
