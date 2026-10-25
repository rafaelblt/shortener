---
status: open
resolution:
labels: [question, domain]
---

# 0031: Generated slugs come from a generator that isn't cryptographically secure

Opened on 2026-10-24.

`Slug.generate()` (`shortener/domain/slug.py`) picks the characters with `random.choices`, of the module `random`, as [Slug](../architecture/domain.md#slug) says. Its generator, the Mersenne Twister, isn't meant for security: the Python documentation says it shouldn't be used for it, and its state can, in principle, be recovered from enough of its outputs, and then its next outputs predicted. Security linters flag it, such as the rule `B311` of Bandit.

A client that creates short URLs without a slug sees the slugs a process of the API generates. From enough of them, it could predict the slugs that process generates next, for other users, and resolve them, since resolving a slug needs no access token, and so learn their target URLs before their owners share them. Each process has its own generator, seeded when it starts.

[Slugs](../service/api.md#slugs) says that a generated slug is "6 random ASCII letters and digits", but nothing says whether it has to be unpredictable. Whether the service guarantees that, such as by generating the slugs with the module `secrets`, is still to be decided.
