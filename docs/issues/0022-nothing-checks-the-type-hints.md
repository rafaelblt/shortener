---
status: open
resolution:
labels: [question, api, infra, bootstrap]
---

# 0022: Nothing checks the type hints

Opened on 2026-10-16.

[CONTRIBUTING.md](../../CONTRIBUTING.md#3-readability) asks for type hints, but nothing checks that they are right. Whether to adopt a type checker, which one, and over which code, is still to be decided. This issue records what [mypy](https://mypy-lang.org/) 2.4.0 found when it was tried on commit `8d504a1`, with its default settings over `shortener/`, `tests/` and `alembic/`, so that the decision can start from it.

mypy reports 27 errors in 15 files.

## In the code

Some of them say that a type hint doesn't match what the code does:

- `shortener/bootstrap/app.py:48`: `SQLAlchemyUnitOfWork` isn't a `UnitOfWork`, since its `begin()` returns `_AsyncGeneratorContextManager[SQLAlchemyTransaction, None]` and the protocol expects `AbstractAsyncContextManager[Transaction, bool | None]`.
- `shortener/api/endpoints.py:36`, `:39`, `:44` and `:50`: `Redirect`, `Created`, `JSONContent` and `NoContent` aren't a `SuccessResponse`, since the protocol declares `status_code` as a settable attribute and they expose it read-only. `shortener/api/endpoint.py:55` has the same error for the default `JSONContent()`.
- `shortener/api/endpoint.py`: `"type" has no attribute "execute"` at lines 111 and 145, a missing return statement at line 74, and `__init__` accessed on an instance at line 72.
- `shortener/infra/db/shorturl_repository.py:176`: `__cause__` is accessed on a value typed `BaseException | None`.
- `shortener/infra/db/transient_errors.py:55`: a `BaseException | None` is assigned to a variable typed `Exception`.
- `shortener/infra/db/shorturl_repository.py:137`: `tuple_()` receives a `datetime` and a `UUID`, which the stubs of SQLAlchemy don't accept. It may be a limit of the stubs rather than of the code.

## In the tests and the dependencies

- Tests that pass a value of the wrong type on purpose, to check what the code does with it: `tests/test_domain/test_entity_id.py:21`, `tests/test_domain/test_shorturl.py:27`, `tests/test_infra/test_jwt_access_token_verifier.py:154` and `tests/test_use_cases/test_list_shorturls.py:98`.
- Methods with an empty body in the classes of `tests/test_api/test_endpoint.py` (lines 44, 58 and 64).
- `tests/test_bootstrap/conftest.py:3` imports a fixture `uow` whose type differs from a fixture of the same name.
- `tests/test_bootstrap/test_app.py:173`: `dict()` of the rows of a query.
- asyncpg has no type hints, so its imports are reported (`shortener/infra/db/transient_errors.py`, `tests/test_infra/test_db/test_transient_errors.py` and `tests/test_infra/test_db/test_health_check.py`), and PyYAML needs the package `types-PyYAML` (`tests/utils/openapi_helpers.py`).
