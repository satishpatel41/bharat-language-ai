---
name: add-language
description: Add or change a supported language in Bharat Language AI. Use when asked to support a new Indian language or dialect.
---

1. Add a `Language(code, name, native_name, script, whisper_code)` entry in `backend/app/languages.py`, keeping the tuple sorted by code. Omit `whisper_code` if Whisper has no support (audio then auto-detects).
2. Use the lowercase ISO 639 code.
3. Update `tests/test_languages.py` if the set of expected codes changes.
4. Run the `run-checks` skill.
5. Update the language note in `README.md` if the count changes.
