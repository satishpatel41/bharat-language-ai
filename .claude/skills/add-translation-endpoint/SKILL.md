---
name: add-translation-endpoint
description: Add a new translation input type or endpoint (for example PDF or document). Use when extending the API beyond text, image, audio and video.
---

1. Add a request/response model in `backend/app/schemas.py`.
2. Put the logic in a new module under `backend/app/services/`. Depend on the `Translator` / `SpeechToText` protocols only. If a new provider capability is needed, add it to `providers/base.py`, implement it in `providers/claude.py`, and add it to `tests/fakes.py`.
3. Add the route in `backend/app/routers/translate.py`, enforcing a size limit via `app/uploads.py` and a limit setting in `config.py`.
4. Write tests in `backend/tests/` (service test plus an API test through `test_api.py` patterns) with fakes, no network.
5. Document the endpoint in the `README.md` table and run the `run-checks` skill.
