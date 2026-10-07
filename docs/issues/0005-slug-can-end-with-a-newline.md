---
status: closed
resolution: fixed
labels: [bug, domain]
---

# 0005: A slug can end with a newline

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

In `shortener/domain/shorturl/fields/slug.py`, `SLUG_PATTERN` is `^[a-zA-Z0-9_-]+$`, and `Slug.validate_slug()` checks it with `re.match`. In Python, `$` also matches right before a trailing `\n`, so a slug ending with a newline passes, and the newline counts toward its length:

```python
Slug("abc\n")  # <Slug('abc\n')>, len 4
```

Expected, from the message of `ShortURLInvalidSlugError` ("Allowed: a-z, A-Z, 0-9, _, -"): `ShortURLInvalidSlugError`.

## 2026-10-07: Closed as fixed

`Slug.create()` checks `SLUG_PATTERN` with `StringValidation.matches()`, which uses `fullmatch`, so the whole value has to match and `Slug.create("abc\n")` returns `Err` with the `INVALID_FORMAT` issue. Tested in `tests/test_domain/test_shorturl/test_slug/test_create.py`.
