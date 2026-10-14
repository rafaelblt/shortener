---
status: open
resolution:
labels: [todo, use_cases, infra]
---

# 0017: The events of deleted users aren't processed

Opened on 2026-10-13.

The README (Owner) and `docs/domain.md#owner` say that, when a user is deleted, an external event will trigger the deletion of their short URLs. Nothing does it yet: no use case deletes the short URLs of an owner, `ShortURLRepository` has no method that does it, and nothing receives the events. Until then, the short URLs of a deleted user keep working forever, and not only for the window `docs/domain.md#owner` accepts. Left out of the scope of the restructuring of the outer layers.

How the events arrive, such as a message broker or an endpoint the issuer of the tokens calls, and so which layers receive them, are still to be decided.
