import pytest
import pytest_asyncio

from datetime import datetime, timezone

from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.refresh_token import RefreshToken
from shortener.domain.refresh_token.exceptions import RefreshTokenNotFoundError

from shortener.domain.user.user import User
from shortener.infra.db.repositories import SQLAlchemyRefreshTokenRepository

from tests.utils.entity_helpers import get_persistent_user, assert_refresh_token_fields


@pytest_asyncio.fixture
async def repository(sqlalchemy_refresh_token_repository):
    return sqlalchemy_refresh_token_repository


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyRefreshTokenRepository,
    normal_user: User,
    active_refresh_token: RefreshToken
):
    saved_user = await get_persistent_user(
        session=repository.session,
        user=normal_user
    )
    active_refresh_token._user = saved_user

    retrieved = await repository.add(active_refresh_token)
    assert isinstance(retrieved, RefreshToken)
    assert retrieved.pk.get_id() == 1
    assert_refresh_token_fields(retrieved, active_refresh_token, ignore_pk=True)


@pytest.mark.asyncio
async def test_get_by_pk(
    repository: SQLAlchemyRefreshTokenRepository,
    normal_user: User,
    active_refresh_token: RefreshToken
):
    saved_user = await get_persistent_user(
        session=repository.session,
        user=normal_user
    )
    active_refresh_token._user = saved_user

    saved_token = await repository.add(active_refresh_token)

    retrieved = await repository.get_by_pk(saved_token.pk)

    assert isinstance(retrieved, RefreshToken)
    assert_refresh_token_fields(retrieved, saved_token)


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyRefreshTokenRepository, 
    normal_user: User,
    poor_user: User,
    active_refresh_token: RefreshToken
):
    saved_user = await get_persistent_user(
        session=repository.session,
        user=normal_user
    )
    active_refresh_token._user = saved_user

    saved_token = await repository.add(active_refresh_token)

    other_user = await get_persistent_user(session=repository.session, user=poor_user)
    saved_token._token = "new_token"
    saved_token._user = other_user
    saved_token._expires_at = datetime(3000, month=5, day=29, tzinfo=timezone.utc)
    saved_token._created_at = datetime(3000, month=5, day=29, tzinfo=timezone.utc)
    saved_token._revoked = True

    retrieved = await repository.update(saved_token)

    assert isinstance(retrieved, RefreshToken)
    assert_refresh_token_fields(retrieved, saved_token)

    updated_token = await repository.get_by_pk(saved_user.pk)
    assert isinstance(updated_token, RefreshToken)
    assert_refresh_token_fields(updated_token, saved_token)


@pytest.mark.asyncio
async def test_update_entity_without_id_raises_error(
    repository: SQLAlchemyRefreshTokenRepository,
    active_refresh_token: RefreshToken
):
    with pytest.raises(ValueError, match="The pk is not of type id"):
        await repository.update(active_refresh_token)


@pytest.mark.asyncio
async def test_update_entity_non_existent_raises_error(
    repository: SQLAlchemyRefreshTokenRepository,
    active_refresh_token: RefreshToken
):
    active_refresh_token._pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(RefreshTokenNotFoundError) as error:
        await repository.update(active_refresh_token)
    assert error.value.value == active_refresh_token.pk
    assert error.value.field == "pk"


@pytest.mark.asyncio
async def test_get_by_token(
    repository: SQLAlchemyRefreshTokenRepository,
    normal_user: User,
    active_refresh_token: RefreshToken
):
    saved_user = await get_persistent_user(
        session=repository.session,
        user=normal_user
    )
    active_refresh_token._user = saved_user

    saved_token = await repository.add(active_refresh_token)

    retrieved = await repository.get_by_token(saved_token.token)
    
    assert isinstance(retrieved, RefreshToken)
    assert_refresh_token_fields(retrieved, saved_token)
