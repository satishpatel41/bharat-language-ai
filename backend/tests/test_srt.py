import pytest

from app.services.srt import format_srt, format_timestamp


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "00:00:00,000"),
        (1.5, "00:00:01,500"),
        (61.001, "00:01:01,001"),
        (3661.25, "01:01:01,250"),
        (-3, "00:00:00,000"),
    ],
)
def test_format_timestamp(seconds, expected):
    assert format_timestamp(seconds) == expected


def test_format_srt_numbers_cues_and_trims_text():
    srt = format_srt([(0, 1.5, " Hello "), (1.5, 3, "World")])
    assert srt == (
        "1\n00:00:00,000 --> 00:00:01,500\nHello\n\n2\n00:00:01,500 --> 00:00:03,000\nWorld\n"
    )


def test_format_srt_empty():
    assert format_srt([]) == ""
