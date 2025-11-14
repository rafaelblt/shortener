import pytest

from datetime import datetime, timezone

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared import PaginatedResult

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, OriginalURL, ShortURLStatus
from shortener.domain.shorturl.exceptions import ShortURLNotFoundError

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository

from tests.utils.entity_helpers import assert_shorturl_fields


@pytest.fixture
def repository(sqlalchemy_shorturl_repository):
    return sqlalchemy_shorturl_repository


@pytest.mark.asyncio
async def test_add(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    retrieved = await repository.add(normal_shorturl)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_pk=True)

    saved_model = await repository.session.get(ShortURLModel, retrieved.pk.get_id())
    assert saved_model is not None
    assert saved_model.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_update(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):  
    saved_shorturl = await repository.add(normal_shorturl)

    saved_shorturl._slug = Slug("test-new-updated-slug")
    saved_shorturl._original_url = OriginalURL("https://target.com")
    saved_shorturl._status = ShortURLStatus.BANNED
    saved_shorturl._visit_count = 5
    saved_shorturl._created_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    saved_shorturl._expires_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    saved_shorturl._last_accessed_at = datetime(2000, 1, 1, tzinfo=timezone.utc)

    updated_shorturl = await repository.update(saved_shorturl)

    assert isinstance(updated_shorturl, ShortURL)
    assert_shorturl_fields(updated_shorturl, saved_shorturl)


@pytest.mark.asyncio
async def test_update_shorturl_non_existent_raises_error(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(ShortURLNotFoundError) as error:
        await repository.update(normal_shorturl)
    assert error.value.field == "pk"
    assert error.value.value == normal_shorturl.pk


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
    await repository.add(normal_shorturl)
    await repository.add(other_shorturl)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], ShortURL)
        assert retrieved[i].pk.get_id() == expected_id
    assert_shorturl_fields(retrieved[0], normal_shorturl, ignore_pk=True)
    assert_shorturl_fields(retrieved[1], other_shorturl, ignore_pk=True)


@pytest.mark.asyncio
async def test_get_by_pk(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):  
    shorturl = await repository.add(normal_shorturl)

    retrieved = await repository.get_by_pk(shorturl.pk)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_pk=True)


@pytest.mark.asyncio
async def test_get_by_slug(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):  
    await repository.add(normal_shorturl)

    retrieved = await repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_pk=True)


@pytest.mark.asyncio
async def test_list_paginated(
    repository: SQLAlchemyShortURLRepository, 
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
    old_shorturl: ShortURL
):
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
async def test_delete_by_pk(
    repository: SQLAlchemyShortURLRepository, normal_shorturl: ShortURL
):
    shorturl = await repository.add(normal_shorturl)

    retrieved = await repository.delete_by_pk(shorturl.pk)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert_shorturl_fields(retrieved, normal_shorturl, ignore_pk=True)
    assert await repository.exists_by_slug(normal_shorturl.slug) == False


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_shorturl(
    repository: SQLAlchemyShortURLRepository
):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(ShortURLNotFoundError) as error:
        await repository.delete_by_pk(pk)
    assert error.value.field == "pk"
    assert error.value.value == pk
