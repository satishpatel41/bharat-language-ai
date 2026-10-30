# Bharat Language AI

FastAPI backend that translates text, photos, audio and video between Indian languages (22 scheduled languages + English).

## Layout
- `backend/app/routers/translate.py`: HTTP endpoints under `/api`
- `backend/app/services/`: text, image, media (audio/video), srt, ffmpeg logic
- `backend/app/providers/`: `base.py` protocols (`Translator`, `SpeechToText`), `claude.py`, `whisper_stt.py`
- `backend/app/languages.py`: the supported language table
- `backend/tests/`: pytest; `fakes.py` has fake providers

## Commands (run in `backend/`)
- Install: `pip install -e ".[dev]"`
- Test: `pytest --cov`
- Lint: `ruff check . && ruff format --check .`

## Rules
- Python must stay compatible with 3.11 (no `def f[T]` syntax); CI tests 3.11-3.13.
- Services depend on provider protocols, never on Claude or Whisper directly.
- Tests must not hit the network or need `ANTHROPIC_API_KEY`; use `tests/fakes.py`.
- Raise `AppError` subclasses from `app/errors.py` so the API returns clean messages.
- Keep coverage at or above 85%. Never commit `.env`.
- Language codes are lowercase ISO 639 (`gu`, `hi`, `brx`); `auto` means detect the source.

## Skills
See `.claude/skills/`: `add-language`, `add-translation-endpoint`, `run-checks`.
