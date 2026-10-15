from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from shortener.api.app import create_app as create_api
from shortener.bootstrap.settings import AccessTokenSettings, Settings, SettingsError
from shortener.bootstrap.use_cases import UseCases
from shortener.infra.clock import UTCClock
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
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

    # The engine connects only when it is first used, and pre_ping replaces
    # the connections the server closed while they waited in the pool.
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        await engine.dispose()

    use_cases = UseCases(
        uow=SQLAlchemyUnitOfWork(engine),
        shorturls=SQLAlchemyShortURLReader(engine),
        clock=UTCClock(),
    )
    return create_api(
        use_cases=use_cases,
        access_token_verifier=access_token_verifier(settings.access_tokens),
        lifespan=lifespan,
    )


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
