---
status: open
resolution:
labels: [bug, domain]
---

# 0011: Copying a parsed value object that breaks the rules raises `ValueError`

Opened on 2026-10-10.

`Slug.parse()` and `TargetURL.parse()` accept a value that breaks the rules of `create()`, such as a slug created under older rules. But copying or pickling the instance they return raises `ValueError`:

```python
import copy
import pickle

slug = Slug.parse("ab")
copy.copy(slug)                   # ValueError: ValidationError(issues=(ValidationIssue(code=<IssueCode.TOO_SHORT: 'too_short'>),))
copy.deepcopy(slug)               # the same ValueError
pickle.loads(pickle.dumps(slug))  # the same ValueError

copy.deepcopy(TargetURL.parse("http://example.com"))  # ValueError, with INVALID_FORMAT
```

`Slug` and `TargetURL` (`shortener/domain/slug.py` and `shortener/domain/target_url.py`) are `str` subclasses that don't define how they are copied or pickled, so `copy` and `pickle` rebuild them with `__new__(cls, value)`. Their `__new__` runs the rules of `create()`, and raises `ValueError` when the value breaks them. A `ShortURL` that holds such a value can't be copied either.

No code of the service copies or pickles them. The tests of the use cases copy short URLs with `record_copies()` (`tests/fixtures/use_cases/doubles.py`), so they can't use one that holds such a value.

Expected, from `docs/domain.md`: "a value accepted under older rules has to keep working". How a copy should rebuild the instance is still to be decided.
