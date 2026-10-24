---
status: closed
resolution: fixed
labels: [todo, infra]
---

# 0023: The downgrades of the migrations aren't tested

Opened on 2026-10-16.

The tests only run the migrations up: the fixture `database_url` (`tests/fixtures/infra/database.py`) applies `alembic upgrade head` to the Postgres of the tests, and `tests/test_infra/test_db/test_migrations.py` checks that the result has the tables `shortener/infra/db/tables.py` describes ([Migrations](../infra.md#migrations)). No test runs the `downgrade()` of a migration, so one that fails, or that leaves behind something its `upgrade()` created, is only found when someone runs `alembic downgrade`.

A test in `tests/test_infra/test_db/test_migrations.py` could migrate a database up to the last migration, down to the first state and up again, and check that each step works and that the result still has the tables `tables.py` describes. Since it would be one more test, it would run with `poetry run task test_layers`, locally and in the CI, without a step of its own in the workflow: the CI would also check the downgrades, and a migration with a broken downgrade would fail before it is merged.

Whether the test checks only the whole round trip or each migration on its own, and whether it uses the Postgres the whole session shares or one of its own, are still to be decided.

## 2026-10-20: Rolling back a deploy needs the downgrades

Since the processes [only start on a database with exactly the migrations of their code](../service/running.md#checking-the-migrations), rolling back a deploy that migrated the database needs the downgrade of its migrations first, or the processes of the previous version don't start. A broken downgrade would then be found when the rollback is under way. The documents of the service don't say how to roll back a version.

Two things written above changed:

- The task `poetry run task test_layers` no longer exists. The tests run with `poetry run task test`, which `poetry run task check` runs, locally and in the CI (see [Checks](../../CONTRIBUTING.md#checks)).
- The fixture `database_url` applies the migrations with `apply_migrations()` (`shortener/infra/db/migrations.py`), which runs the same `upgrade` to `head`.

The downgrade of the only migration today, `f913103e988f`, was run by hand on a Postgres 17 in a container, with `alembic.command`: up to `head`, down to `base` and up again. Down left only the table `alembic_version`, and up again left no difference from the tables `tables.py` describes. Then, with `alembic_version` set to a migration the code doesn't know, `check_migrations()` raised `UnexpectedMigrationsError`, as it would for the previous version after a rollback. With a single migration, checking the whole round trip and each migration on its own are the same for now.

## 2026-10-24: Closed as fixed

`tests/test_infra/test_db/test_migrations.py` tests the downgrades, with two tests for each migration of `alembic/`, on a database of its own beside the one the session shares, from the fixture `empty_database_url`, migrated up to the migration before it:

- `test_the_downgrade_of_a_migration_leaves_the_tables_as_they_were_before_it` applies the migration, downgrades it, and checks that the tables are as they were before it.
- `test_a_migration_downgraded_applies_again_with_the_same_tables` applies the migration, downgrades it, applies it again, and checks that the tables are as they were after it the first time.

Of the ways above, the tests check each migration on its own, since a rollback downgrades only the migrations of the newer version ([issue 0027](0027-the-documents-dont-say-how-to-roll-back-a-version.md)), and in a round trip down to the first state, what the downgrade of a later migration leaves behind could go away with the downgrade of an earlier one, such as the one that drops its table. They compare the tables with `compare_metadata()` of Alembic, as the test of the tables of `tables.py` already did: to the tables the database had before, which `reflect_tables()` (`tests/fixtures/infra/database.py`) reads, and which `differences_from_the_tables()` now receives. So they don't check what Alembic doesn't compare, such as the check constraints and the defaults of the columns, but a downgrade that leaves something behind that makes its migration fail when it applies again, such as a type, fails the second test. The tests run with `poetry run task test`, so the CI runs them too. `docs/architecture/infra.md`, in Migrations, describes them.

They were checked by breaking the downgrade of `f913103e988f` on purpose: one that does nothing, one that leaves the table, and one that fails each failed both tests, and an upgrade that also created a type that its downgrade left failed the second one. With a second migration that adds a column, copied into `alembic/versions/` only for the check, the four tests passed, and with its downgrade leaving the column, the two of that migration failed, while those of `f913103e988f` passed.
