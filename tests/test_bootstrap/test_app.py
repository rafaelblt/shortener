import asyncio
import httpx
import jwt
import pytest

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlalchemy import text
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

from shortener.api.endpoints import ENDPOINTS
from shortener.bootstrap.app import access_token_verifier, create_app, database_engine
from shortener.bootstrap.settings import (
    DEFAULT_RATE_LIMIT_WINDOW,
    AccessTokenSettings,
    DatabaseSettings,
    RateLimitSettings,
    Settings,
    SettingsError,
)
from shortener.domain import UserID
from shortener.use_cases.unavailable_error import UnavailableError


SECRET = "a-secret-long-enough-for-hs256-signatures"
KEY_SETTINGS = AccessTokenSettings(
    algorithms=("HS256",),
    issuer="https://issuer.example.com",
    audience="shortener",
    key=SECRET,
    jwks_url=None,
)
SETTINGS = Settings(
    database=DatabaseSettings(
        url="postgresql+asyncpg://user:password@localhost:5432/shortener"
    ),
    access_tokens=KEY_SETTINGS,
)


def paths_of(app: FastAPI) -> set[str]:
    return {route.path for route in app.routes if isinstance(route, APIRoute)}


def hs256_token(user_id: UserID, expires_at: datetime) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "iss": KEY_SETTINGS.issuer,
            "aud": KEY_SETTINGS.audience,
            "exp": expires_at,
        },
        SECRET,
        algorithm="HS256",
    )


def test_create_app_returns_the_api_with_every_endpoint():
    assert paths_of(create_app(SETTINGS)) == {
        f"/v1{endpoint.path}" for endpoint in ENDPOINTS
    }


def test_create_app_without_settings_reads_them_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("DATABASE_URL", SETTINGS.database.url)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_ISSUER", KEY_SETTINGS.issuer)
    monkeypatch.setenv("JWT_AUDIENCE", KEY_SETTINGS.audience)
    monkeypatch.setenv("JWT_KEY", SECRET)
    monkeypatch.delenv("JWT_JWKS_URL", raising=False)

    assert paths_of(create_app()) == paths_of(create_app(SETTINGS))


def test_create_app_raises_for_settings_that_cannot_verify_tokens():
    settings = Settings(
        database=SETTINGS.database,
        access_tokens=AccessTokenSettings(
            algorithms=("HS256",),
            issuer=KEY_SETTINGS.issuer,
            audience=KEY_SETTINGS.audience,
            key="short",
            jwks_url=None,
        ),
    )

    with pytest.raises(ValueError):
        create_app(settings)


async def test_create_app_limits_the_requests_of_each_ip_address_by_the_settings():
    settings = replace(
        SETTINGS, rate_limit=RateLimitSettings(requests=1, window=timedelta(hours=1))
    )
    transport = httpx.ASGITransport(app=create_app(settings))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Without an access token, the use case answers without the database.
        within_the_limit = await client.get("/v1/shorturls")
        over_the_limit = await client.get("/v1/shorturls")

    assert within_the_limit.status_code == HTTPStatus.UNAUTHORIZED
    assert over_the_limit.status_code == HTTPStatus.TOO_MANY_REQUESTS
    # Longer than the default window, so the window is the one of the settings.
    retry_after = int(over_the_limit.headers["Retry-After"])
    assert retry_after > DEFAULT_RATE_LIMIT_WINDOW.total_seconds()


async def test_the_application_disposes_its_engine_when_it_stops(
    monkeypatch: pytest.MonkeyPatch,
):
    engine = Mock(dispose=AsyncMock())
    monkeypatch.setattr(
        "shortener.bootstrap.app.create_async_engine", Mock(return_value=engine)
    )
    app = create_app(SETTINGS)

    async with app.router.lifespan_context(app):
        engine.dispose.assert_not_awaited()

    engine.dispose.assert_awaited_once()


async def test_database_engine_sets_the_lock_and_statement_timeouts_of_its_connections(
    database_url: str,
):
    # Postgres keeps them in whole milliseconds, so a fraction rounds up.
    engine = database_engine(
        DatabaseSettings(
            database_url,
            lock_timeout=timedelta(microseconds=100),
            statement_timeout=timedelta(seconds=1.5),
        )
    )
    try:
        async with engine.connect() as connection:
            settings = await connection.execute(
                text(
                    "SELECT name, setting FROM pg_settings"
                    " WHERE name IN ('lock_timeout', 'statement_timeout')"
                )
            )
            assert dict(settings.all()) == {
                "lock_timeout": "1",
                "statement_timeout": "1500",
            }
    finally:
        await engine.dispose()


async def test_database_engine_waits_for_a_free_connection_up_to_the_pool_timeout(
    database_url: str,
):
    engine = database_engine(
        DatabaseSettings(
            database_url,
            pool_size=1,
            max_overflow=1,
            pool_timeout=timedelta(milliseconds=100),
        )
    )
    try:
        async with engine.connect(), engine.connect():
            # The default pool timeout, 30 seconds, would outlast this one.
            async with asyncio.timeout(5):
                with pytest.raises(PoolTimeoutError):
                    await engine.connect().start()
    finally:
        await engine.dispose()


async def test_database_engine_waits_to_connect_up_to_the_connect_timeout(
    silent_server: str,
):
    engine = database_engine(
        DatabaseSettings(
            f"postgresql+asyncpg://user:password@{silent_server}/database",
            connect_timeout=timedelta(milliseconds=100),
        )
    )
    try:
        # The default timeout of asyncpg, 60 seconds, would outlast this one.
        async with asyncio.timeout(5):
            with pytest.raises(TimeoutError):
                await engine.connect().start()
    finally:
        await engine.dispose()


async def test_access_token_verifier_with_a_key_verifies_the_tokens_it_signed(
    owner_id: UserID,
):
    token = hs256_token(owner_id, datetime.now(timezone.utc) + timedelta(hours=1))
    assert await access_token_verifier(KEY_SETTINGS).verify(token) == owner_id


async def test_access_token_verifier_allows_the_leeway_of_the_settings(
    owner_id: UserID,
):
    token = hs256_token(owner_id, datetime.now(timezone.utc) - timedelta(seconds=30))
    lenient = replace(KEY_SETTINGS, leeway=timedelta(seconds=60))
    strict = replace(KEY_SETTINGS, leeway=timedelta(0))

    assert await access_token_verifier(lenient).verify(token) == owner_id
    assert await access_token_verifier(strict).verify(token) is None


async def test_access_token_verifier_with_a_jwks_url_fetches_the_keys_from_it():
    settings = AccessTokenSettings(
        algorithms=("RS256",),
        issuer=KEY_SETTINGS.issuer,
        audience=KEY_SETTINGS.audience,
        key=None,
        jwks_url="http://127.0.0.1:1/jwks.json",
    )
    token = jwt.encode({"sub": "user"}, SECRET, algorithm="HS256", headers={"kid": "1"})

    with pytest.raises(UnavailableError):
        await access_token_verifier(settings).verify(token)


async def test_access_token_verifier_waits_for_the_jwks_url_up_to_the_jwks_timeout(
    silent_server: str,
):
    settings = AccessTokenSettings(
        algorithms=("RS256",),
        issuer=KEY_SETTINGS.issuer,
        audience=KEY_SETTINGS.audience,
        key=None,
        jwks_url=f"http://{silent_server}/jwks.json",
        jwks_timeout=timedelta(milliseconds=100),
    )
    token = jwt.encode({"sub": "user"}, SECRET, algorithm="HS256", headers={"kid": "1"})

    # The default timeout of PyJWT, 30 seconds, would outlast this one.
    async with asyncio.timeout(5):
        with pytest.raises(UnavailableError):
            await access_token_verifier(settings).verify(token)


def test_access_token_verifier_raises_without_a_key_or_a_jwks_url():
    settings = AccessTokenSettings(
        algorithms=("HS256",),
        issuer=KEY_SETTINGS.issuer,
        audience=KEY_SETTINGS.audience,
        key=None,
        jwks_url=None,
    )

    with pytest.raises(SettingsError):
        access_token_verifier(settings)
