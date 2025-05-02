import pytest
import pytest_asyncio

from datetime import datetime, timezone

from tests.utils.entity_helpers import get_persistent_user, assert_shorturl_fields

from shortener.domain.shared import PaginatedResult

from shortener.domain.user import User

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL, ShortURLStatus
from shortener.domain.shorturl.exceptions import ShortURLNotFoundInDatabaseError

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@pytest_asyncio.fixture
async def repository(sqlalchemy_shorturl_repository):
    return sqlalchemy_shorturl_repository


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)

    retrieved = await repository.add(normal_shorturl)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_id=True)

    saved_model = await repository.session.get(ShortURLModel, retrieved.id)
    assert saved_model.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyShortURLRepository,
    normal_shorturl: ShortURL,
    old_user: User
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)
    
    saved_shorturl = await repository.add(normal_shorturl)

    old_user.change_plan(owner.plan)
    old_user = await get_persistent_user(repository.session, old_user)
    saved_shorturl._slug = Slug("test-new-updated-slug")
    saved_shorturl._original_url = URL("https://target.com")
    saved_shorturl._owner = old_user
    saved_shorturl._status = ShortURLStatus.BANNED
    saved_shorturl._visit_count = 5
    saved_shorturl._created_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    saved_shorturl._expires_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    saved_shorturl._last_accessed_at = datetime(2000, 1, 1, tzinfo=timezone.utc)

    updated_shorturl = await repository.update(saved_shorturl)

    assert isinstance(updated_shorturl, ShortURL)
    assert_shorturl_fields(updated_shorturl, saved_shorturl)
    

@pytest.mark.asyncio
async def test_update_shorturl_without_id_raises_error(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    with pytest.raises(
        ShortURLNotFoundInDatabaseError,
        match=f"ShortURL with id={normal_shorturl.id} not found in database."
    ):
        await repository.update(normal_shorturl)


@pytest.mark.asyncio
async def test_update_shorturl_non_existent_raises_error(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    normal_shorturl._id = 1

    with pytest.raises(
        ShortURLNotFoundInDatabaseError, 
        match=f"ShortURL with id={normal_shorturl.id} not found in database."
    ):
        await repository.update(normal_shorturl)


@pytest.mark.asyncio
async def test_get_all_with_no_shorturls(
    repository: SQLAlchemyShortURLRepository
):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_shorturls(
    repository: SQLAlchemyShortURLRepository, 
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)
    other_shorturl.change_owner(owner)

    await repository.add(normal_shorturl)
    await repository.add(other_shorturl)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], ShortURL)
        assert retrieved[i].id == expected_id
    assert_shorturl_fields(retrieved[0], normal_shorturl, ignore_id=True)
    assert_shorturl_fields(retrieved[1], other_shorturl, ignore_id=True)


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)
    
    await repository.add(normal_shorturl)

    retrieved = await repository.get_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_id=True)


@pytest.mark.asyncio
async def test_get_by_slug(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)
    
    await repository.add(normal_shorturl)

    retrieved = await repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_id=True)


@pytest.mark.asyncio
async def test_list_paginated(
    repository: SQLAlchemyShortURLRepository, 
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
    old_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)

    normal_shorturl.change_owner(owner)
    other_shorturl.change_owner(owner)
    old_shorturl.change_owner(owner)

    await repository.add(normal_shorturl)
    await repository.add(other_shorturl)
    await repository.add(old_shorturl)

    retrieved = await repository.list_paginated(offset=0, limit=2)

    assert isinstance(retrieved, PaginatedResult)
    assert len(retrieved.items) == 2
    assert retrieved.offset == 0
    assert retrieved.limit == 2
    assert retrieved.total == 3
    assert retrieved.current_page == 1
    for entity in retrieved.items:
        assert isinstance(entity, ShortURL)


@pytest.mark.asyncio
async def test_exists_by_slug_true(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)

    await repository.add(normal_shorturl)

    retrieved = await repository.exists_by_slug(normal_shorturl.slug)
    assert retrieved == True


@pytest.mark.asyncio
async def test_exists_by_slug_false(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    retrieved = await repository.exists_by_slug(normal_shorturl.slug)
    assert retrieved == False


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    owner = await get_persistent_user(repository.session, normal_shorturl.owner)
    normal_shorturl.change_owner(owner)

    await repository.add(normal_shorturl)

    retrieved = await repository.delete_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_id=True)
    assert await repository.exists_by_slug(normal_shorturl.slug) == False


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_shorturl(
    repository: SQLAlchemyShortURLRepository
):
    with pytest.raises(
        ShortURLNotFoundInDatabaseError, 
        match=f"ShortURL with id=1 not found in database."
    ):
        await repository.delete_by_id(1)
