import asyncio

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import httpx
import jwt
import pytest

from fastapi import FastAPI
from fastapi.routing import APIRoute

from shortener.api.endpoints import ENDPOINTS
from shortener.bootstrap.app import access_token_verifier, create_app
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
from tests.fixtures.infra.database import differences_from_the_tables


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
UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://user:password@127.0.0.1:1/database"


def paths_of(app: FastAPI) -> set[str]:
    return {route.path for route in app.routes if isinstance(route, APIRoute)}


async def check_health(settings: Settings) -> httpx.Response:
    """Asks the application of the settings for its health, then stops it."""
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.get("/health")


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


def test_create_app_returns_the_api_with_every_endpoint_and_the_health_check():
    assert paths_of(create_app(SETTINGS)) == {
        f"/api/v1{endpoint.path}" for endpoint in ENDPOINTS
    } | {"/health"}


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
        within_the_limit = await client.get("/api/v1/shorturls")
        over_the_limit = await client.get("/api/v1/shorturls")

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
        "shortener.bootstrap.database.create_async_engine", Mock(return_value=engine)
    )
    app = create_app(SETTINGS)

    async with app.router.lifespan_context(app):
        engine.dispose.assert_not_awaited()

    engine.dispose.assert_awaited_once()


@pytest.mark.parametrize(
    "migrate_on_start, migrated",
    [
        pytest.param(True, True, id="migrate on start"),
        pytest.param(False, False, id="don't migrate on start"),
    ],
)
async def test_the_application_migrates_its_database_when_it_starts_if_set(
    empty_database_url: str, migrate_on_start: bool, migrated: bool
):
    database = DatabaseSettings(empty_database_url, migrate_on_start=migrate_on_start)
    app = create_app(replace(SETTINGS, database=database))

    async with app.router.lifespan_context(app):
        differences = await differences_from_the_tables(empty_database_url)

    assert (differences == []) is migrated


async def test_the_health_check_passes_when_its_database_answers(database_url: str):
    settings = replace(SETTINGS, database=DatabaseSettings(database_url))

    assert (await check_health(settings)).status_code == HTTPStatus.NO_CONTENT


async def test_the_health_check_fails_when_its_database_is_unreachable():
    settings = replace(SETTINGS, database=DatabaseSettings(UNREACHABLE_DATABASE_URL))

    assert (await check_health(settings)).status_code == HTTPStatus.SERVICE_UNAVAILABLE


async def test_access_token_verifier_with_a_key_verifies_the_tokens_it_signed(
    owner_id: UserID,
):
    token = hs256_token(owner_id, datetime.now(UTC) + timedelta(hours=1))
    assert await access_token_verifier(KEY_SETTINGS).verify(token) == owner_id


async def test_access_token_verifier_allows_the_leeway_of_the_settings(
    owner_id: UserID,
):
    token = hs256_token(owner_id, datetime.now(UTC) - timedelta(seconds=30))
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
