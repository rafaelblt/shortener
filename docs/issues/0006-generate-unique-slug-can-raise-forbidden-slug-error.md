---
status: open
resolution:
labels: [bug, domain]
---

# 0006: `generate_unique_slug()` can raise `ShortURLForbiddenSlugError`

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

`Slug.generate_random()` returns its result as a `Slug`, which validates it. With the default length of 6, it can produce `config` or `logout` in any letter case, which are in `FORBIDDEN_SLUGS`. That is 128 of the 62⁶ possible slugs, so it is rare.

When it happens inside `generate_unique_slug()` (`shortener/domain/shorturl/utils.py`), the `ShortURLForbiddenSlugError` escapes, instead of counting as a failed attempt.

To reproduce:

```python
with patch("random.choices", return_value=list("LogOut")):
    Slug.generate_random()  # ShortURLForbiddenSlugError
```

Expected, from the docstring of `generate_unique_slug()`: a unique slug, or `RuntimeError` when every attempt fails.
