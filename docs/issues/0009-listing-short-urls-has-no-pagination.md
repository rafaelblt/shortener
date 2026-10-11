---
status: closed
resolution: fixed
labels: [question, use_cases]
---

# 0009: Listing short URLs has no pagination

Opened on 2026-10-10.

`ListShortURLs` (`shortener/use_cases/list_shorturls.py`) returns every short URL of the user making the request, in a single tuple, read with `ShortURLReader.list_by_owner()` (`shortener/use_cases/shorturl_repository.py`). The more short URLs a user has, the larger the response, with no limit.

Whether listing should be paginated is still to be decided, before the v1, and, if it should, of which kind: offset and limit, or a cursor. Either kind needs an order, and the contract of `list_by_owner()` doesn't define one yet.

## 2026-10-11: Closed as fixed

Listing is paginated by cursor. `ListShortURLs.execute(limit, cursor)` returns a `ShortURLPage`, with up to `limit` short URLs and the `ShortURLCursor` where the next page starts, or `None` when there is no next page. `limit` is 20 by default, and from 1 to 100: another value returns `InvalidInputError`, checked with the new `IntegerValidation` of `shared/`. `list_by_owner()` now takes a `limit` and an `after` cursor, and defines the order: newest first, by `created_at` descending, then by `id` descending. See `docs/use_cases.md#listshorturls`.
