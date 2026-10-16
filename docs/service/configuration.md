# Configuration

The service is configured by environment variables, and only by them: it doesn't read a `.env` file, which uvicorn can load with `--env-file`. The API and the consumer of the events read different variables. How the code reads them is in [the architecture of bootstrap](../architecture/bootstrap.md#settings), and how to run each process, in [Running](running.md).

## The API

| Variable         | Required       | Value                                                                                                                                                                                     |
| ---------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`   | Yes            | The URL of the Postgres database, with the driver asyncpg, such as `postgresql+asyncpg://user:password@localhost:5432/shortener`. The [migrations](running.md#the-processes) read it too. |
| `JWT_ALGORITHMS` | Yes            | The algorithms an access token may be signed with, separated by commas, such as `RS256` or `HS256`                                                                                        |
| `JWT_ISSUER`     | Yes            | The issuer of the tokens, which their `iss` has to be                                                                                                                                     |
| `JWT_AUDIENCE`   | Yes            | The audience of the tokens, which their `aud` has to be or have                                                                                                                           |
| `JWT_KEY`        | One of the two | The key that verifies the tokens: the secret of the HMAC algorithms, or the public key of the others, in PEM                                                                              |
| `JWT_JWKS_URL`   | One of the two | The URL where the issuer publishes the keys that verify the tokens, as a JWKS                                                                                                             |

And these optional ones, whose values are numbers:

| Variable                     | Default | Value                                                                                                                                         |
| ---------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_POOL_SIZE`         | 5       | The connections to the database each process keeps open: 1 or more                                                                            |
| `DATABASE_MAX_OVERFLOW`      | 10      | The connections each process opens beyond `DATABASE_POOL_SIZE` when those are all in use, and closes when they are returned: 0 or more        |
| `DATABASE_POOL_TIMEOUT`      | 30      | The most a request waits for a connection when they are all in use, in seconds: more than 0                                                   |
| `DATABASE_CONNECT_TIMEOUT`   | 10      | The most the service waits to connect to the database, in seconds: more than 0                                                                |
| `DATABASE_LOCK_TIMEOUT`      | 5       | The most a statement waits for a lock, such as the one of a short URL another request is changing, in seconds: more than 0, up to 2147483.647 |
| `DATABASE_STATEMENT_TIMEOUT` | 30      | The most a statement runs, in seconds: more than 0, up to 2147483.647                                                                         |
| `JWT_LEEWAY`                 | 60      | The difference allowed between the clocks of the issuer of the tokens and of the service, in seconds: 0 or more                               |
| `JWT_JWKS_TIMEOUT`           | 5       | The most the service waits for each step of fetching the keys from `JWT_JWKS_URL`, in seconds: more than 0. Only with `JWT_JWKS_URL`          |
| `RATE_LIMIT_REQUESTS`        | 60      | The requests each IP address can make in each window of `RATE_LIMIT_WINDOW`: 1 or more (see [Rate limit](api.md#rate-limit))                  |
| `RATE_LIMIT_WINDOW`          | 60      | The window of time of `RATE_LIMIT_REQUESTS`, in seconds: more than 0                                                                          |

When one of the timeouts of the database runs out, the request that waited answers `503` with `unavailable`, and the consumer tries its message again (see [Handling](events.md#handling)).

## The consumer

The consumer of the events has no access tokens or rate limit, so it doesn't read their variables:

| Variable       | Required | Value                                                                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL` | Yes      | The same as in the API                                                                                                |
| `RABBITMQ_URL` | Yes      | The URL of RabbitMQ, `amqp` or `amqps`, such as `amqp://user:password@localhost:5672/`, where `/` is the virtual host |

It reads the optional variables of the database, from `DATABASE_POOL_SIZE` to `DATABASE_STATEMENT_TIMEOUT`, as the API does, with the same defaults and rules.

## How the values are read

- Spaces at the ends of a value are removed, and an empty value is the same as a variable that isn't set.
- In `JWT_ALGORITHMS`, an empty item between commas is left out.
- A number of seconds may have decimals, such as `0.5`, and the other numbers are whole.

## Errors when starting

A process doesn't start when its variables don't make valid settings. It stops with a single error that names every problem it found:

- a required variable that is missing;
- a `DATABASE_URL` that isn't a URL of `postgresql+asyncpg`, or a `RABBITMQ_URL` that isn't `amqp` or `amqps`;
- both or neither of `JWT_KEY` and `JWT_JWKS_URL`, or `JWT_JWKS_TIMEOUT` with `JWT_KEY`;
- an optional variable that isn't a number, or is out of the range of its table.

The API also doesn't start when the settings of the access tokens can't verify tokens:

- an algorithm that isn't supported, or `none`;
- a key that doesn't suit one of the algorithms, such as a public key as the secret of an HMAC algorithm, or a secret shorter than the hash of its algorithm;
- a `JWT_JWKS_URL` that isn't `http` or `https`.

The rest is found later, when it is used:

- The database is first reached by the first request, or the first message. When it can't be reached, they answer `503`, and when it fails in a way that trying again won't fix, such as a wrong password or a database that doesn't exist, the request answers `500`, and the message goes to the dead-letter queue.
- The keys of `JWT_JWKS_URL` are first fetched by the first request with an access token.
- The consumer doesn't start when RabbitMQ can't be reached. After it starts, it connects again by itself, every 5 seconds, when the connection is lost.

## The defaults

- `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW` and `DATABASE_POOL_TIMEOUT` have the defaults of SQLAlchemy, and `DATABASE_CONNECT_TIMEOUT` is 10 seconds, instead of the 60 of asyncpg.
- `DATABASE_LOCK_TIMEOUT` and `DATABASE_STATEMENT_TIMEOUT` have a default because Postgres has none: without them, a statement waits for a lock, and runs, as long as it takes. 2147483.647 seconds is the most Postgres takes for them, which it keeps as a number of milliseconds in an `int`, and it takes them in whole milliseconds, so a fraction of a millisecond rounds up.
- `JWT_LEEWAY` is a setting because the right value depends on the clock of the issuer of each environment.
- `JWT_JWKS_TIMEOUT` is 5 seconds by default, instead of the 30 of PyJWT, since each fetch of the keys holds a thread of the service while it waits. Setting it with `JWT_KEY` is an error, since it is more likely a mistake of whoever set the variables.
