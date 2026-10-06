---
status: open
resolution:
labels: [bug, domain]
---

# 0003: Value objects don't check that the value is a string

Opened on 2026-10-06. Moved from the known problems of `docs/domain.md`.

`Slug`, `URL` and `OriginalURL` are typed `value: str`, but don't check it, and a value of another type has a different outcome in each one:

```python
Slug(12345)         # Slug('12345'): converted with str() and accepted
URL(123)            # AttributeError: 'int' object has no attribute 'decode'
OriginalURL(123)    # AttributeError: 'int' object has no attribute 'decode'
URL(None)           # InvalidURLError
```

`Slug.__new__` (`shortener/domain/shorturl/fields/slug.py`) calls `str(value)` before validating. `URL.__new__` (`shortener/domain/shared/valueobjects/url.py`) passes the value to `urlparse`, and only catches `ValueError` and `TypeError`.

Which error a value that isn't a string should raise is still to be decided.

## 2026-10-06: `URL` and `OriginalURL` replaced by `TargetURL`

`URL` and `OriginalURL` no longer exist: `TargetURL` (`shortener/domain/shorturl/fields/target_url.py`) replaced both. It also passes the value to `urlparse` and only catches `ValueError` and `TypeError`, so the problem remains for `Slug` and `TargetURL`:

```python
TargetURL(123)      # AttributeError: 'int' object has no attribute 'decode'
TargetURL(None)     # ShortURLInvalidURLError
```
