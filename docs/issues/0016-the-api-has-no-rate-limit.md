---
status: open
resolution:
labels: [todo, api]
---

# 0016: The API has no rate limit

Opened on 2026-10-13.

Nothing limits how many requests a client makes, to any endpoint: creating short URLs, or resolving slugs, where each resolution writes to the database. Left out of the scope of the restructuring of the outer layers.

Which endpoints to limit, by what (the user of the token, the IP address), with which limits, and whether in the service or in a proxy in front of it, as with the domain of short links (`docs/api.md#endpoints`), are still to be decided.
