import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.infra.settings import settings
from shortener.infra.services.refresh_token import SQLAlchemyRefreshAuthTokenService


@pytest.fixture
def sqlalchemy_refresh_auth_token_service(sqlalchemy_session: AsyncSession):
    return SQLAlchemyRefreshAuthTokenService(
        session=sqlalchemy_session,
        expires_in=settings.refresh_token_expiration
    )
