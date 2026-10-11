---
status: open
resolution:
labels: [bug, infra]
---

# 0007: Concurrent resolutions can lose increments of `resolution_count`

Opened on 2026-10-08.

`ShortURL.resolve()` counts the resolution in memory: it adds 1 to the `resolution_count` it was loaded with. If the short URL is persisted by saving it whole back to the database, two requests that resolve the same slug at the same time both load the same `resolution_count`, both add 1, and both save the same value. One of the resolutions is lost.

The current `SQLAlchemyShortURLRepository.update()` (`shortener/infra/db/repositories/shorturl_repository.py`) works like that: it copies every field of the entity to the model, `visit_count` and `last_accessed_at` included (the old names of `resolution_count` and `last_resolved_at`), with no atomic increment and no version check. The current use case doesn't count resolutions yet, so it doesn't happen today. It will happen once a use case calls `resolve()` and saves the short URL through a repository that works the same way.

Expected, from `docs/domain.md`: `resolution_count` is the number of times `resolve()` returned `target_url`. How the infra guarantees it (an atomic increment, optimistic locking or something else) is still to be decided.

## 2026-10-10: The use case of resolutions reads through the transaction

`ResolveSlug` (`shortener/use_cases/resolve_slug.py`) now counts the resolution with `resolve()` and saves the whole short URL with `save()`, so the problem described above can happen once `infra` implements the use cases' abstractions. To prevent it, the use case reads the short URL through the `Transaction` it saves in, and the contract of `Transaction` (`docs/use_cases.md`, in Concurrency) says that a short URL read through a transaction can't be changed by another transaction until the first one ends, and that another transaction reading it waits, and then reads what was written. With the contract kept, two concurrent resolutions of the same slug run one after the other, and the count goes up by 2.

Still to do, in the phase of `infra`: keeping that contract, and testing it with two concurrent transactions that resolve the same slug. From the planning of the use cases: `SELECT ... FOR UPDATE` in the reads of a transaction on Postgres, and `BEGIN IMMEDIATE` in the transactions of the unit of work on SQLite, which has no `FOR UPDATE`.
