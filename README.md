# Bharat Language AI

[![CI](https://github.com/satishpatel41/bharat-language-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/satishpatel41/bharat-language-ai/actions/workflows/ci.yml)

AI translation across Indian languages. Send **text, photos, audio or video** and get the translation back.
Covers the 22 scheduled languages of India plus English.

| Input | Endpoint | What you get |
|-------|----------|--------------|
| Text  | `POST /api/translate/text`  | Translated text and detected source language |
| Photo | `POST /api/translate/image` | Text read from the image, plus its translation |
| Audio | `POST /api/translate/audio` | Transcript, per-segment translation, SRT subtitles |
| Video | `POST /api/translate/video` | Same as audio, after extracting the audio track with ffmpeg |
| -     | `GET /api/languages`        | Supported languages and whether speech input works for each |
| -     | `GET /health`               | Liveness check |

## How it works

- **Translation and image reading:** Claude (model set by `CLAUDE_MODEL`).
- **Speech to text:** local [faster-whisper](https://github.com/SYSTRAN/faster-whisper), opt-in via the `audio` extra.
  Languages Whisper does not support (for example Bodo, Dogri, Santali) fall back to auto-detect.
- **Design:** services depend on the `Translator` and `SpeechToText` protocols in
  `backend/app/providers/base.py`, so providers can be swapped and tests use fakes.

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # add ",audio" for speech recognition
cp .env.example .env               # set ANTHROPIC_API_KEY
uvicorn app.main:app --reload      # docs at http://localhost:8000/docs
```

Audio and video need `ffmpeg` on the PATH. Docker bundles it:

```bash
docker build -t bharat-language-ai backend
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=... bharat-language-ai
```

Example:

```bash
curl -X POST localhost:8000/api/translate/text \
  -H 'content-type: application/json' \
  -d '{"text": "Hello, how are you?", "target_language": "gu"}'
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | - | Required for translation |
| `CLAUDE_MODEL` | `claude-sonnet-5-5` | Model used |
| `WHISPER_MODEL` | `small` | Whisper size for audio and video |

Upload limits, ffmpeg timeout and CORS origins live in `backend/app/config.py`.

## Tests and CI

```bash
cd backend
pytest --cov          # unit tests, no network or API key needed
ruff check . && ruff format --check .
```

- `.github/workflows/ci.yml`: lint, tests on Python 3.11-3.13 (coverage gate 85%), Docker build.
- `.github/workflows/cd.yml`: after CI passes on `main`, publishes the image to `ghcr.io/satishpatel41/bharat-language-ai`.

## Working with Claude

`CLAUDE.md` describes the project for Claude Code, and `.claude/skills/` holds repeatable workflows:
`add-language`, `add-translation-endpoint`, `run-checks`.

## Roadmap

- Web and mobile client
- Text-to-speech for translated output
- Translation quality evaluation sets per language
