---
name: run-checks
description: Run lint, format check and unit tests for the backend the same way CI does. Use before committing or pushing.
---

From `backend/`:

1. `ruff check .`
2. `ruff format --check .` (fix with `ruff format .`)
3. `pytest --cov --cov-fail-under=85`

Fix failures before committing. If tests need the network or an API key, the test is wrong: use `tests/fakes.py`.
Also confirm no 3.12-only syntax was added (CI runs Python 3.11).
