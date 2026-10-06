---
status: open
resolution:
labels: [refactor, domain]
---

# 0004: `URL` and `OriginalURL` duplicate their validation

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

Each class writes the same validation twice, once in `__new__` and once in the `validate()` class method:

- `URL` (`shortener/domain/shared/valueobjects/url.py`): both parse the value with `_parse_url()` and raise `InvalidURLError` when the scheme or the netloc is empty.
- `OriginalURL` (`shortener/domain/shorturl/fields/url.py`): both convert `InvalidURLError` into `ShortURLInvalidURLError`, and raise it when the scheme isn't `https`.

AGENTS.md asks for each rule to be written in one place.
