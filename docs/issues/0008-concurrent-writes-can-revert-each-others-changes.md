---
status: open
resolution:
labels: [bug, use_cases, infra]
---

# 0008: Concurrent writes to a short URL can revert each other's changes

Opened on 2026-10-10.

When a short URL is persisted by saving it whole, a write based on a version loaded before a concurrent change was saved writes back the old values of the fields that change replaced. Issue 0007 is one case of this, for `resolution_count`. The others revert changes to the other fields:

- Two requests update the same short URL at the same time, one changing only the slug and the other only the target URL. Both load the same version, and the one that saves last writes back the old value of the field the other one changed.
- A resolution and a deactivation of the same short URL happen at the same time. The resolution loads the short URL while it is still `ACTIVE`, the deactivation saves it as `DEACTIVATED`, and then the resolution saves it with the changes of `resolve()` and the `ACTIVE` it loaded. The short URL is active again without `enable()` being called.

`UpdateShortURLUseCase` (`shortener/use_cases/update_shorturl.py`) loads the short URL with `get_by_pk()`, changes it and saves it with `SQLAlchemyShortURLRepository.update()` (`shortener/infra/db/repositories/shorturl_repository.py`), which copies every field of the entity to the model, with no lock and no version check. The first case follows from that. The second also needs a use case that deactivates short URLs and one that saves the short URL after `resolve()`, and neither exists yet. None of it happens today: `use_cases` and `infra` still import modules the restructuring of the domain removed, such as `shortener.domain.shared`, and fail to load.

Expected, from `docs/domain.md`: a short URL only goes from `DEACTIVATED` to `ACTIVE` through `enable()`. Nothing defines it for the other fields yet. How the upper layers prevent it (a lock, a version check, saving only the changed fields or something else) is still to be decided.
