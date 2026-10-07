---
status: closed
resolution: obsolete
labels: [bug, domain]
---

# 0001: The slug length error messages are swapped

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

In `shortener/domain/shorturl/exceptions.py`, the messages of the two slug length errors have "at least" and "at most" swapped:

- `ShortURLSlugTooShortError`: "Slug must be at most {min_length} characters long."
- `ShortURLSlugTooLongError`: "Slug must be at least {max_length} characters long."

To reproduce:

```python
Slug("ab")      # [SLUG_TOO_SHORT]: Slug must be at most 3 characters long.
Slug("a" * 31)  # [SLUG_TOO_LONG]: Slug must be at least 30 characters long.
```

Expected, from the error codes and the limits they carry: "at least 3" for `SLUG_TOO_SHORT`, and "at most 30" for `SLUG_TOO_LONG`.

## 2026-10-07: Closed as obsolete

The slug length errors were removed, along with their messages. `Slug.create()` now returns the broken rules in a `ValidationError`, as issues that only have a code: `TOO_SHORT` or `TOO_LONG`.
