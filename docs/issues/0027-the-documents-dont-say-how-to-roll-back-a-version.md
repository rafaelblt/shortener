---
status: open
resolution:
labels: [todo, docs]
---

# 0027: The documents don't say how to roll back a version

Opened on 2026-10-20.

[Checking the migrations](../service/running.md#checking-the-migrations) in `docs/service/running.md` says that a version of the service only starts on a database with exactly its migrations, and that a process of the old version doesn't start on a database that a newer one migrated. So rolling back a deploy that migrated the database needs the migrations of the newer version to be downgraded first, with `alembic downgrade` and the `DATABASE_URL` of the environment, or the processes of the previous version don't start. [`DATABASE_MIGRATE_ON_START`](../service/running.md#migrating-on-start) only upgrades.

No document of the service says this, nor how to roll back a version: which migration to downgrade to, which command runs it, and in which order with the deploy of the previous version. A downgrade that drops a table or a column also drops its data. The downgrades themselves aren't tested ([issue 0023](0023-the-downgrades-of-the-migrations-arent-tested.md)).

What the documents say about rolling back, and whether the service should offer more than `alembic downgrade` for it, is still to be decided.
