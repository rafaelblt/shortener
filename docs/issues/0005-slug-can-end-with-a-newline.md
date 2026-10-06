---
status: open
resolution:
labels: [bug, domain]
---

# 0005: A slug can end with a newline

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

In `shortener/domain/shorturl/fields/slug.py`, `SLUG_PATTERN` is `^[a-zA-Z0-9_-]+$`, and `Slug.validate_slug()` checks it with `re.match`. In Python, `$` also matches right before a trailing `\n`, so a slug ending with a newline passes, and the newline counts toward its length:

```python
Slug("abc\n")  # <Slug('abc\n')>, len 4
```

Expected, from the message of `ShortURLInvalidSlugError` ("Allowed: a-z, A-Z, 0-9, _, -"): `ShortURLInvalidSlugError`.
