---
status: open
resolution:
labels: [question, domain]
---

# 0030: A target URL has no maximum length

Opened on 2026-10-24.

`TargetURL.create()` (`shortener/domain/target_url.py`) has no rule on the length of the value (see [TargetURL](../architecture/domain.md#targeturl)), and the column `target_url` is `text`, with no limit, on purpose (see [The shorturls table](../architecture/infra.md#the-shorturls-table)). So a user can store a target URL as long as the body of the request allows, which nothing limits either ([issue 0029](0029-the-api-reads-a-body-of-any-size-and-one-that-isnt-json-skips-the-rate-limit.md)). For example, `TargetURL.create("https://example.com/" + "a" * 50 * 1024 * 1024)` returns `Ok`.

Such a target URL is stored, answered in every listing and resolution, and sent in the `Location` header of the redirect, where proxies and clients usually refuse headers much shorter than that. Together with [issue 0028](0028-a-user-can-have-any-number-of-short-urls.md), nothing bounds what a user can store.

[Target URLs](../service/api.md#target-urls) gives no maximum, while a slug has one (see [Slugs](../service/api.md#slugs)). Whether a target URL has a maximum length, and which, is still to be decided.
