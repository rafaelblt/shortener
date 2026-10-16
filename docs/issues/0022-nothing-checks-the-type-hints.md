---
status: closed
resolution: fixed
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

## 2026-10-16: Closed as fixed

mypy checks the type hints, with `poetry run task typecheck`, as `pyproject.toml` configures it:

- `shortener/` and `alembic/` with its strict mode, so every function of the code has type hints, and they are checked.
- The tests with its strict mode too, but without needing type hints, and with the bodies of the functions that have none checked. They compare values of different types and pass values of the wrong type on purpose, and their doubles return `Any`, so `strict_equality` and `warn_return_any` are off for them, and so is `empty-body`, for the classes of `tests/test_api/test_endpoint.py`, which only have signatures.
- asyncpg has no type hints, so its imports aren't checked, and `types-PyYAML` has the ones of PyYAML.

What it found was fixed:

- `SuccessResponse` and `Transaction` declare `status_code` and `shorturls` as read-only properties, so their implementations, whose attributes are read-only or of a subtype, implement them, and `SQLAlchemyUnitOfWork` is a `UnitOfWork`.
- `Endpoint.use_case` is a `type[UseCase]`, a `Protocol` of `shortener/api/endpoint.py` whose `execute()` returns a `Result`, so the endpoint knows the types of what it runs.
- `is_transient()` keeps the error of a `DBAPIError` in a variable of its own, `_is_slug_taken()` handles an `IntegrityError` without `orig`, and `_select_by_owner()` compares the columns with a tuple of values instead of `tuple_()` of values.
- The functions of the domain that had no type hints have them.
- In the tests, each value of the wrong type passed on purpose is typed `Any` or has a `type: ignore` with its code, and `tests/test_bootstrap/conftest.py` imports from `tests.fixtures.infra` only the fixtures the tests of bootstrap use, since its `uow` and the one of `tests.fixtures.use_cases` have the same name.
