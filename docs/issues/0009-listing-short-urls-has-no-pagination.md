---
status: open
resolution:
labels: [question, use_cases]
---

# 0009: Listing short URLs has no pagination

Opened on 2026-10-10.

`ListShortURLs` (`shortener/use_cases/list_shorturls.py`) returns every short URL of the user making the request, in a single tuple, read with `ShortURLReader.list_by_owner()` (`shortener/use_cases/shorturl_repository.py`). The more short URLs a user has, the larger the response, with no limit.

Whether listing should be paginated is still to be decided, before the v1, and, if it should, of which kind: offset and limit, or a cursor. Either kind needs an order, and the contract of `list_by_owner()` doesn't define one yet.
