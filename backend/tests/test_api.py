from __future__ import annotations

import io

from tests.conftest import PNG_BYTES


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"


def test_languages_endpoint_lists_all(client):
    languages = client.get("/api/languages").json()
    by_code = {lang["code"]: lang for lang in languages}
    assert len(languages) == 23
    assert by_code["hi"]["native_name"] == "हिन्दी"
    assert by_code["hi"]["speech_input"] is True
    assert by_code["brx"]["speech_input"] is False


def test_translate_text(client):
    response = client.post("/api/translate/text", json={"text": "Hello", "target_language": "gu"})
    assert response.status_code == 200
    assert response.json()["translated_text"] == "[gu] Hello"


def test_translate_text_blank_is_rejected(client):
    response = client.post("/api/translate/text", json={"text": "  ", "target_language": "gu"})
    assert response.status_code == 422


def test_translate_text_unknown_language_is_422(client):
    response = client.post("/api/translate/text", json={"text": "Hi", "target_language": "xx"})
    assert response.status_code == 422
    assert "Unsupported language" in response.json()["detail"]


def test_translate_text_too_long_is_rejected(client):
    response = client.post(
        "/api/translate/text", json={"text": "a" * 10_001, "target_language": "hi"}
    )
    assert response.status_code == 422


def test_translate_image(client, png_file):
    response = client.post(
        "/api/translate/image",
        files={"file": ("sign.png", png_file, "image/png")},
        data={"target_language": "en"},
    )
    assert response.status_code == 200
    assert response.json()["extracted_text"] == "नमस्ते"


def test_translate_image_rejects_non_image(client):
    response = client.post(
        "/api/translate/image",
        files={"file": ("doc.png", io.BytesIO(b"%PDF-1.7"), "image/png")},
        data={"target_language": "en"},
    )
    assert response.status_code == 415


def test_translate_image_enforces_size_limit(client):
    big = io.BytesIO(PNG_BYTES + b"\x00" * 2048)
    response = client.post(
        "/api/translate/image",
        files={"file": ("big.png", big, "image/png")},
        data={"target_language": "en"},
    )
    assert response.status_code == 413


def test_translate_audio(client):
    response = client.post(
        "/api/translate/audio",
        files={"file": ("clip.mp3", io.BytesIO(b"fake audio"), "audio/mpeg")},
        data={"target_language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_language"] == "hi"
    assert len(body["segments"]) == 2
    assert body["srt"].startswith("1\n00:00:00,000")


def test_translate_audio_rejects_bad_extension(client):
    response = client.post(
        "/api/translate/audio",
        files={"file": ("clip.exe", io.BytesIO(b"x"), "application/octet-stream")},
        data={"target_language": "en"},
    )
    assert response.status_code == 415


def test_translate_audio_enforces_size_limit(client):
    response = client.post(
        "/api/translate/audio",
        files={"file": ("clip.mp3", io.BytesIO(b"x" * 2048), "audio/mpeg")},
        data={"target_language": "en"},
    )
    assert response.status_code == 413


def test_translate_video_rejects_bad_extension(client):
    response = client.post(
        "/api/translate/video",
        files={"file": ("clip.txt", io.BytesIO(b"x"), "text/plain")},
        data={"target_language": "en"},
    )
    assert response.status_code == 415


def test_translate_video_with_unreadable_file_is_422_or_501(client):
    response = client.post(
        "/api/translate/video",
        files={"file": ("clip.mp4", io.BytesIO(b"not a video"), "video/mp4")},
        data={"target_language": "en"},
    )
    # 422 when ffmpeg is installed, 501 when it is not.
    assert response.status_code in {422, 501}
