---
status: open
resolution:
labels: [todo, api]
---

# 0014: The API has no health check

Opened on 2026-10-13.

`ENDPOINTS` (`shortener/api/endpoints.py`) only has the endpoints of the use cases (see `docs/api.md#endpoints`), so nothing tells an orchestrator or a load balancer whether the service is up and able to answer. Left out of the scope of the restructuring of the outer layers.

The path, whether it checks the database or only that the process answers, and whether it is under `/v1`, are still to be decided.
