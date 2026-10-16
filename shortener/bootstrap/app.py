import math

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from shortener.api.app import create_app as create_api
from shortener.bootstrap.settings import (
    AccessTokenSettings,
    DatabaseSettings,
    Settings,
    SettingsError,
)
from shortener.bootstrap.use_cases import UseCases
from shortener.infra.clock import UTCClock
from shortener.infra.db.health_check import SQLAlchemyHealthCheck
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
from shortener.infra.in_memory_rate_limiter import InMemoryRateLimiter
from shortener.infra.jwt_access_token_verifier import JWTAccessTokenVerifier


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    The application, with the settings, or with the ones of the environment
    variables when there are none. Uvicorn runs it as a factory.
    See docs/bootstrap.md#running

    Raises:
        SettingsError: The environment variables don't make valid settings.
        ValueError: The settings of the access tokens can't verify tokens.
    """
    if settings is None:
        settings = Settings.from_environment()

    engine = database_engine(settings.database)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        await engine.dispose()

    clock = UTCClock()
    use_cases = UseCases(
        uow=SQLAlchemyUnitOfWork(engine),
        shorturls=SQLAlchemyShortURLReader(engine),
        clock=clock,
    )
    return create_api(
        use_cases=use_cases,
        access_token_verifier=access_token_verifier(settings.access_tokens),
        rate_limiter=InMemoryRateLimiter(
            settings.rate_limit.requests, settings.rate_limit.window, clock
        ),
        health_check=SQLAlchemyHealthCheck(engine),
        lifespan=lifespan,
    )


def database_engine(settings: DatabaseSettings) -> AsyncEngine:
    """
    The engine of the database, with the pool and the timeouts of the
    settings. See docs/bootstrap.md#the-application
    """
    # The engine connects only when it is first used, and pre_ping replaces
    # the connections the server closed while they waited in the pool.
    return create_async_engine(
        settings.url,
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout.total_seconds(),
        connect_args={
            "timeout": settings.connect_timeout.total_seconds(),
            "server_settings": {
                "lock_timeout": _milliseconds(settings.lock_timeout),
                "statement_timeout": _milliseconds(settings.statement_timeout),
            },
        },
    )


def _milliseconds(time: timedelta) -> str:
    # Postgres takes these timeouts in whole milliseconds, and 0 turns them
    # off, so a fraction of a millisecond rounds up.
    return f"{math.ceil(time / timedelta(milliseconds=1))}ms"


def access_token_verifier(settings: AccessTokenSettings) -> JWTAccessTokenVerifier:
    """
    Raises:
        SettingsError: The settings have neither a key nor a JWKS URL.
        ValueError: The settings can't verify tokens.
    """
    if settings.jwks_url is not None:
        return JWTAccessTokenVerifier.with_jwks(
            settings.jwks_url,
            settings.algorithms,
            settings.issuer,
            settings.audience,
            settings.leeway,
            settings.jwks_timeout,
        )
    if settings.key is not None:
        return JWTAccessTokenVerifier.with_key(
            settings.key,
            settings.algorithms,
            settings.issuer,
            settings.audience,
            settings.leeway,
        )
    raise SettingsError("The settings of the access tokens need a key or a JWKS URL")
