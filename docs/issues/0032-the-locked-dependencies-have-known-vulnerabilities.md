---
status: open
resolution:
labels: [todo, api]
---

# 0032: The locked dependencies have known vulnerabilities

Opened on 2026-10-24.

`uvx pip-audit` on the dependencies that `poetry.lock` installs without the group `dev` finds known vulnerabilities in 9 of them, among them:

| Package            | Locked    | Fixed in   | Vulnerabilities                                                                              |
| ------------------ | --------- | ---------- | -------------------------------------------------------------------------------------------- |
| `starlette`        | 0.45.3    | 1.3.1      | 7, such as CVE-2025-54121, CVE-2025-62727 and CVE-2026-48710, on forms, files and the `Host` |
| `python-multipart` | 0.0.20    | 0.0.31     | 6, on parsing forms                                                                          |
| `h11`              | 0.14.0    | 0.16.0     | CVE-2025-43859, request smuggling with chunked bodies                                        |
| `anyio`            | 4.8.0     | 4.14.2     | 2                                                                                            |
| `idna`             | 3.10      | 3.15       | CVE-2026-45409, a denial of service                                                          |
| `certifi`          | 2025.1.31 | 2026.10.19 | GHSA-6q48-6c7w-9gw2, a root certificate whose intermediates were compromised                 |

The others are `mako`, `pygments` and `python-dotenv`, on code the service doesn't run. Most of them don't reach the service either: it parses no forms, serves no files, and uvicorn parses HTTP with `httptools`, which `fastapi[standard]` installs, and not with `h11`. `starlette` is held at 0.45 by the constraint of `fastapi`, `>=0.115.8,<0.116.0`, in `pyproject.toml`.

Still to do: updating the dependencies, `fastapi` first, and checking them again with `pip-audit`.
