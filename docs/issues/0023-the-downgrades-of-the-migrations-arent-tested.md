---
status: open
resolution:
labels: [todo, infra]
---

# 0023: The downgrades of the migrations aren't tested

Opened on 2026-10-16.

The tests only run the migrations up: the fixture `database_url` (`tests/fixtures/infra/database.py`) applies `alembic upgrade head` to the Postgres of the tests, and `tests/test_infra/test_db/test_migrations.py` checks that the result has the tables `shortener/infra/db/tables.py` describes ([Migrations](../infra.md#migrations)). No test runs the `downgrade()` of a migration, so one that fails, or that leaves behind something its `upgrade()` created, is only found when someone runs `alembic downgrade`.

A test in `tests/test_infra/test_db/test_migrations.py` could migrate a database up to the last migration, down to the first state and up again, and check that each step works and that the result still has the tables `tables.py` describes. Since it would be one more test, it would run with `poetry run task test_layers`, locally and in the CI, without a step of its own in the workflow: the CI would also check the downgrades, and a migration with a broken downgrade would fail before it is merged.

Whether the test checks only the whole round trip or each migration on its own, and whether it uses the Postgres the whole session shares or one of its own, are still to be decided.
