---
status: closed
resolution: fixed
labels: [todo, api, infra, bootstrap]
---

# 0014: The API has no health check

Opened on 2026-10-13.

`ENDPOINTS` (`shortener/api/endpoints.py`) only has the endpoints of the use cases (see `docs/api.md#endpoints`), so nothing tells an orchestrator or a load balancer whether the service is up and able to answer. Left out of the scope of the restructuring of the outer layers.

The path, whether it checks the database or only that the process answers, and whether it is under `/v1`, are still to be decided.

## 2026-10-15: Decided how the health check works

A single route, `GET /v1/health`, checks the database, and not only that the process answers. Its path is `/health`, under `/v1`, like every other route, and it answers `204 No Content` when the service is able to answer.

## 2026-10-15: Closed as fixed

`GET /v1/health` answers `204 No Content` when the database answers, `503 Service Unavailable`, with `unavailable`, when it can't for a transient failure, and `500` for any other error, such as a database that doesn't exist. The API defines the `HealthCheck` abstraction, which `create_app()` receives, and adds the route with `add_health_check_route()`, out of `ENDPOINTS`, since it runs no use case. `SQLAlchemyHealthCheck`, in `infra`, runs `SELECT 1` on a connection of the engine, and `bootstrap` gives it to the API. `docs/api.md`, in Health check, describes it.
