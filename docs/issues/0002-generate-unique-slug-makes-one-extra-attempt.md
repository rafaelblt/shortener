---
status: open
resolution:
labels: [bug, domain]
---

# 0002: `generate_unique_slug()` makes one attempt more than `max_attempts`

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

In `shortener/domain/shorturl/utils.py`, `attempts` starts at 0 and the loop runs `while attempts <= max_attempts`, so `generate_unique_slug()` generates and checks `max_attempts + 1` slugs before raising `RuntimeError`. The error message still says "after {max_attempts} attempts".

To reproduce, with a repository whose `exists_by_slug()` always returns `True`:

```python
await generate_unique_slug(repository, max_attempts=3)
# RuntimeError: Could not generate a unique slug after 3 attempts.
# repository.exists_by_slug was awaited 4 times.
```

Expected, from the parameter name, the docstring and the error message: exactly `max_attempts` attempts.

The tests in `tests/test_domain/test_shorturl/test_slug/test_generate_unique.py` only check the error message, not the number of attempts.
