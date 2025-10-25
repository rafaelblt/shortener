import pytest

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.services.exceptions import TokenExpiredError, TokenInvalidError
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.user import User

from shortener.infra.db.models import RefreshTokenModel, UserModel
from shortener.infra.services.refresh_token import SQLAlchemyRefreshAuthTokenService


TOKEN_SERVICE_EXPIRES_IN = timedelta(days=30)


@pytest.fixture
def token_service(sqlalchemy_session):
    return SQLAlchemyRefreshAuthTokenService(
        session=sqlalchemy_session, expires_in=TOKEN_SERVICE_EXPIRES_IN
    )


def test_class_init(token_service, sqlalchemy_session):
    assert token_service.session == sqlalchemy_session
    assert token_service.expires_in == TOKEN_SERVICE_EXPIRES_IN


@pytest.mark.asyncio
async def test_generate_token(
    token_service: SQLAlchemyRefreshAuthTokenService,
    persistent_normal_user: User,
    sqlalchemy_session: AsyncSession,
):
    retrieved = await token_service.generate_token(persistent_normal_user)
    assert isinstance(retrieved.value, str)
    assert retrieved.purpose == ""
    assert (
        retrieved.created_at.replace(microsecond=0) == 
        utc_now().replace(microsecond=0)
    )
    assert retrieved.expires_at == retrieved.created_at + TOKEN_SERVICE_EXPIRES_IN

    token_saved = await sqlalchemy_session.get(RefreshTokenModel, 1)
    assert token_saved is not None
    assert token_saved.token == retrieved.value
    assert token_saved.created_at == retrieved.created_at.replace(tzinfo=None)
    assert token_saved.expires_at == retrieved.expires_at.replace(tzinfo=None)
    assert token_saved.user_id == persistent_normal_user.pk.get_id()


@pytest.mark.asyncio
async def test_decode_token_raises_token_invalid_with_random_token(
    token_service: SQLAlchemyRefreshAuthTokenService
):
    with pytest.raises(TokenInvalidError):
        await token_service.decode_token("random token")


@pytest.mark.asyncio
async def test_decode_token(
    token_service: SQLAlchemyRefreshAuthTokenService,
    persistent_normal_user: User,
):
    refresh_token = await token_service.generate_token(persistent_normal_user)
    retrieved = await token_service.decode_token(refresh_token.value)
    assert retrieved.pk == persistent_normal_user.pk
    assert retrieved.email == persistent_normal_user.email


@pytest.mark.asyncio
async def test_decode_token_raises_token_invalid_with_revoked_token(
    token_service: SQLAlchemyRefreshAuthTokenService,
    persistent_normal_user: User,
):
    refresh_token = await token_service.generate_token(persistent_normal_user)
    await token_service.decode_token(refresh_token.value)

    with pytest.raises(TokenInvalidError):
        await token_service.decode_token(refresh_token.value)


@pytest.mark.asyncio
async def test_decode_token_raises_token_invalid_with_user_not_found(
    token_service: SQLAlchemyRefreshAuthTokenService,
    persistent_normal_user: User,
    sqlalchemy_session: AsyncSession
):
    refresh_token = await token_service.generate_token(persistent_normal_user)
    await token_service.decode_token(refresh_token.value)
    user_model = await sqlalchemy_session.get(UserModel, persistent_normal_user.pk.get_id())
    assert user_model is not None
    await sqlalchemy_session.delete(user_model)
    await sqlalchemy_session.commit()

    with pytest.raises(TokenInvalidError):
        await token_service.decode_token(refresh_token.value)


@pytest.mark.asyncio
async def test_decode_token_raises_token_expired(
    persistent_normal_user: User,
    sqlalchemy_session: AsyncSession
):
    token_service = SQLAlchemyRefreshAuthTokenService(
        session=sqlalchemy_session, expires_in=timedelta(microseconds=1)
    )
    refresh_token = await token_service.generate_token(persistent_normal_user)

    with pytest.raises(TokenExpiredError):
        await token_service.decode_token(refresh_token.value)
