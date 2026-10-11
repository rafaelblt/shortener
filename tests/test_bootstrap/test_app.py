import jwt
import pytest

from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.routing import APIRoute

from shortener.api.endpoints import ENDPOINTS
from shortener.bootstrap.app import access_token_verifier, create_app
from shortener.bootstrap.settings import AccessTokenSettings, Settings, SettingsError
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
    database_url="postgresql+asyncpg://user:password@localhost:5432/shortener",
    access_tokens=KEY_SETTINGS,
)


def paths_of(app: FastAPI) -> set[str]:
    return {route.path for route in app.routes if isinstance(route, APIRoute)}


def test_create_app_returns_the_api_with_every_endpoint():
    assert paths_of(create_app(SETTINGS)) == {
        f"/v1{endpoint.path}" for endpoint in ENDPOINTS
    }


def test_create_app_without_settings_reads_them_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("DATABASE_URL", SETTINGS.database_url)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_ISSUER", KEY_SETTINGS.issuer)
    monkeypatch.setenv("JWT_AUDIENCE", KEY_SETTINGS.audience)
    monkeypatch.setenv("JWT_KEY", SECRET)
    monkeypatch.delenv("JWT_JWKS_URL", raising=False)

    assert paths_of(create_app()) == paths_of(create_app(SETTINGS))


def test_create_app_raises_for_settings_that_cannot_verify_tokens():
    settings = Settings(
        database_url=SETTINGS.database_url,
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


async def test_access_token_verifier_with_a_key_verifies_the_tokens_it_signed(
    owner_id: UserID,
):
    token = jwt.encode(
        {
            "sub": str(owner_id),
            "iss": KEY_SETTINGS.issuer,
            "aud": KEY_SETTINGS.audience,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        SECRET,
        algorithm="HS256",
    )

    assert await access_token_verifier(KEY_SETTINGS).verify(token) == owner_id


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
