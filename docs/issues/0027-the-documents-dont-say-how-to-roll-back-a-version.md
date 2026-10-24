---
status: closed
resolution: fixed
labels: [todo, docs]
---

# 0027: The documents don't say how to roll back a version

Opened on 2026-10-20.

[Checking the migrations](../service/running.md#checking-the-migrations) in `docs/service/running.md` says that a version of the service only starts on a database with exactly its migrations, and that a process of the old version doesn't start on a database that a newer one migrated. So rolling back a deploy that migrated the database needs the migrations of the newer version to be downgraded first, with `alembic downgrade` and the `DATABASE_URL` of the environment, or the processes of the previous version don't start. [`DATABASE_MIGRATE_ON_START`](../service/running.md#migrating-on-start) only upgrades.

No document of the service says this, nor how to roll back a version: which migration to downgrade to, which command runs it, and in which order with the deploy of the previous version. A downgrade that drops a table or a column also drops its data. The downgrades themselves aren't tested ([issue 0023](0023-the-downgrades-of-the-migrations-arent-tested.md)).

What the documents say about rolling back, and whether the service should offer more than `alembic downgrade` for it, is still to be decided.

## 2026-10-24: Closed as fixed

`docs/service/running.md` says how to roll back a version, in Rolling back a version: when the newer version added migrations, find the last migration of the previous version, with `alembic heads` run with its image, stop the processes of the newer version, downgrade the database to that migration with `alembic downgrade`, run with the image of the newer version and the `DATABASE_URL` of the environment, and start the processes of the previous version. It also says that a downgrade drops the data of the tables and columns it drops, and that one that fails changes nothing. The processes and Checking the migrations link to it, and `docs/architecture/infra.md`, in Migrations, says that the `downgrade()` of a migration is reviewed too.

The service offers no more than `alembic downgrade` for it. A process of the previous version can't downgrade the database, since it doesn't have the migrations to undo, and one of the newer version that downgraded it when it starts would drop data that no one asked to drop. The downgrades are tested since [issue 0023](0023-the-downgrades-of-the-migrations-arent-tested.md).

The steps were run on a Postgres 17 in a container, with a copy of the code that had a second migration, which adds a column to `shorturls`, as the newer version, and the code of `main` as the previous one. After the newer version migrated the database, `check_migrations()` of the previous one raised `UnexpectedMigrationsError`, naming `f913103e988f` as the migration the code expects. `alembic heads` of the previous one printed `f913103e988f (head)` without `DATABASE_URL`, and in the image built from the `Dockerfile` too. `alembic downgrade f913103e988f` failed with the previous one, which can't locate the second migration, and worked with the newer one, after which `check_migrations()` of the previous one passed. A downgrade that failed after dropping the column left the column, its value and the migration of the database as they were. The downgrade that worked kept the row of the short URL, without the column, whose value was gone when the newer version migrated the database up again.
