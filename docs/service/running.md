# Running

How the service runs: its processes, what they need around them, and how to run more than one of each. Their settings are in [Configuration](configuration.md). How the code assembles and starts them is in [the architecture of bootstrap](../architecture/bootstrap.md).

## The processes

The service is two processes, from the same image, which share the Postgres database:

| Process      | Command                                                                           | Needs                                  |
| ------------ | --------------------------------------------------------------------------------- | -------------------------------------- |
| The API      | `uvicorn shortener.bootstrap.app:create_app --factory --host 0.0.0.0 --port 8000` | Postgres, and the issuer of the tokens |
| The consumer | `python -m shortener.bootstrap.consumer`                                          | Postgres and RabbitMQ                  |

- The command of the API is the one of the image, in the [Dockerfile](../../Dockerfile), which listens on the port of the `PORT` environment variable, as platforms such as Cloud Run, Heroku and Render set it, or on 8000 when it isn't set. `poetry run task run` runs it with `--reload`, for development, and `poetry run task consume` runs the consumer.
- They run apart, so a failure of one doesn't stop the other, and each one runs as many processes as it needs.
- The consumer runs until it gets `SIGINT` or `SIGTERM`. A message it hasn't acknowledged by then goes back to the queue, and is handled again.
- The schema of the database is created and changed by the migrations, which `alembic upgrade head` applies, with the `DATABASE_URL` of the environment, or the processes themselves when they start, with [`DATABASE_MIGRATE_ON_START`](#migrating-on-start), and which `alembic downgrade` undoes, to [roll back a version](#rolling-back-a-version). A version of the service only starts on a database with exactly its migrations (see [Checking the migrations](#checking-the-migrations)).

To try the service locally, [Docker Compose](../../README.md#running-with-docker-compose) runs all of it.

## More than one process

- **The API:** each process, such as each worker of uvicorn or each replica, counts its own [rate limit](api.md#rate-limit), so an address can make up to the limit in each one, and keeps its own pool of connections to the database, of up to `DATABASE_POOL_SIZE` plus `DATABASE_MAX_OVERFLOW` connections, which Postgres has to allow for every process together.
- **The consumer:** the processes share the queue, and RabbitMQ delivers each message to only one of them, which handles one message at a time.

## Checking the migrations

When it starts, each process connects to the database, and checks that the last migration the database has is the last one of the code: the API before it answers any request, the health check included, and the consumer before it connects to RabbitMQ. When it isn't, the process doesn't start, with an error that names the migrations of each. So a process doesn't start:

- when the database can't be reached, or refuses the connection, such as for a wrong password;
- when the database is missing migrations, such as when it was never migrated;
- when the database has a migration the code doesn't know, such as one of a newer version of the service. During a deploy that migrates the database, a process of the old version that restarts, such as one the orchestrator replaces, doesn't start again, and neither does the old version when it is deployed again to roll back the newer one, until the database is downgraded (see [Rolling back a version](#rolling-back-a-version)).

## Migrating on start

With `DATABASE_MIGRATE_ON_START` set to `true`, the API and the consumer apply the migrations the database doesn't have yet when they start, before they [check them](#checking-the-migrations). A process whose migrations fail doesn't start.

- Every process that migrates, when it starts or with `alembic upgrade head`, first takes the same lock of Postgres. So when several start at once, such as the replicas of the API and of the consumer, one of them applies the migrations, and the others wait for it, and then find nothing left to apply.
- A process waits for the lock, and for the migrations, as long as they take, without the timeouts of `DATABASE_LOCK_TIMEOUT` and `DATABASE_STATEMENT_TIMEOUT`. An orchestrator that restarts the API when it doesn't answer within some time after it starts may restart it while it migrates.

## Rolling back a version

Going back to the previous version of the service, such as after a deploy that went wrong, is a deploy of its image. When the newer version added no migrations, that is all. When it did, the processes of the previous version [don't start](#checking-the-migrations) on the database the newer one migrated, which has to be downgraded first, to the last migration of the previous version:

1. Find the last migration of the previous version: `alembic heads`, run with its image, prints it, followed by `(head)`, without connecting to the database. A process of the previous version that doesn't start names it too, in its error, as the migration its code expects.
2. Stop the processes of the newer version. One that kept running would find the tables changed under it, and could fail, and one that restarted with `DATABASE_MIGRATE_ON_START` would migrate the database up again.
3. Downgrade the database with `alembic downgrade <migration>`, run with the image of the newer version and the `DATABASE_URL` of the environment. Only the newer version has the migrations to undo: run with the image of the previous one, `alembic downgrade` fails, since it doesn't know them.
4. Start the processes of the previous version.

- A downgrade undoes the migrations with their data: a table or a column it drops takes with it what the newer version stored there, which doesn't come back when the newer version is deployed again. The short URLs the newer version created or changed stay, with what the previous version stores of a short URL.
- The downgrade runs in a single transaction, so one that fails changes nothing, and the database keeps the migrations of the newer version.

## Health checks

[`GET /health`](api.md#health-check) answers `204` when the API can answer, which it checks by asking the database. So, as a liveness probe, one that restarts the service when it fails, a failure of the database restarts the API too. The consumer has no health check.

## Behind a proxy

The [rate limit](api.md#rate-limit) counts the requests of each IP address under the address uvicorn gives as the client's. Behind a proxy, that is the address of the proxy, unless uvicorn trusts it: then it takes the address of the client from the `X-Forwarded-For` header the proxy sends.

- uvicorn trusts the addresses of its `--forwarded-allow-ips` option, or of the `FORWARDED_ALLOW_IPS` environment variable, which are only `127.0.0.1` when neither is set. So behind a proxy at another address, set one of them to the address of the proxy, or every request through it counts under that address.
- Trusting a client that can reach the service without the proxy would let it send any address in `X-Forwarded-For`.
- A request without the address of its client, which uvicorn may give for a connection that isn't TCP, such as one through a Unix socket, has no rate limit.

A domain of short links, where `/{slug}` redirects, is a proxy in front of the service, which sends `/{slug}` to `/api/v1/slugs/{slug}/redirect`. Slugs can't have dots, so a path such as `/favicon.ico` is never the slug of a new short URL. The [health check](#health-checks), `/health`, is the only route of the API out of `/api/v1`, and `health` is a slug like any other, so that proxy sends `/health` to the redirect of the slug: an orchestrator asks the health check at the address of the API, and not through the domain of short links.

## Logs

The processes log to the standard error:

- With [`DATABASE_MIGRATE_ON_START`](#migrating-on-start), the consumer logs, at the level `INFO`, each migration it applies, and the API doesn't log them.

- The API logs a warning for each `503`, with the error and its cause, which say what was unavailable. uvicorn logs the error of each `500`, but the one of the [health check](api.md#health-check), which the API logs, with its traceback.
- The consumer logs, at the level `INFO`, when it starts consuming, a warning for each message it rejects because its body isn't the event, or puts back in the queue, and an error, with its traceback, for each message a failure sends to the dead-letter queue.
