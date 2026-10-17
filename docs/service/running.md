# Running

How the service runs: its processes, what they need around them, and how to run more than one of each. Their settings are in [Configuration](configuration.md). How the code assembles and starts them is in [the architecture of bootstrap](../architecture/bootstrap.md).

## The processes

The service is two processes, from the same image, which share the Postgres database:

| Process      | Command                                                                           | Needs                                  |
| ------------ | --------------------------------------------------------------------------------- | -------------------------------------- |
| The API      | `uvicorn shortener.bootstrap.app:create_app --factory --host 0.0.0.0 --port 8000` | Postgres, and the issuer of the tokens |
| The consumer | `python -m shortener.bootstrap.consumer`                                          | Postgres and RabbitMQ                  |

- The command of the API is the one of the image, in the [Dockerfile](../../Dockerfile). `poetry run task run` runs it with `--reload`, for development, and `poetry run task consume` runs the consumer.
- They run apart, so a failure of one doesn't stop the other, and each one runs as many processes as it needs.
- The consumer runs until it gets `SIGINT` or `SIGTERM`. A message it hasn't acknowledged by then goes back to the queue, and is handled again.
- The schema of the database is created and changed by the migrations, which `alembic upgrade head` applies, with the `DATABASE_URL` of the environment. A new version of the service may need its migrations applied before it starts.

To try the service locally, [Docker Compose](../../README.md#running-with-docker-compose) runs all of it.

## More than one process

- **The API:** each process, such as each worker of uvicorn or each replica, counts its own [rate limit](api.md#rate-limit), so an address can make up to the limit in each one, and keeps its own pool of connections to the database, of up to `DATABASE_POOL_SIZE` plus `DATABASE_MAX_OVERFLOW` connections, which Postgres has to allow for every process together.
- **The consumer:** the processes share the queue, and RabbitMQ delivers each message to only one of them, which handles one message at a time.

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

- The API logs a warning for each `503`, with the error and its cause, which say what was unavailable. uvicorn logs the error of each `500`, but the one of the [health check](api.md#health-check), which the API logs, with its traceback.
- The consumer logs, at the level `INFO`, when it starts consuming, a warning for each message it rejects because its body isn't the event, or puts back in the queue, and an error, with its traceback, for each message a failure sends to the dead-letter queue.
