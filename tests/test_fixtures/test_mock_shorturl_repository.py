import pytest

from shortener.domain.shared.pagination import PaginatedResult
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLNotFoundInDatabaseError

from tests.mocks import MockShortURLRepository


@pytest.fixture
def repository(mock_shorturl_repository) -> MockShortURLRepository:
    return mock_shorturl_repository


def test_to_dict(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    shorturl_dict = repository._to_dict(normal_shorturl)
    assert isinstance(shorturl_dict, dict)
    assert shorturl_dict["id"] == normal_shorturl.id
    assert shorturl_dict["slug"] == normal_shorturl.slug
    assert shorturl_dict["original_url"] == normal_shorturl.original_url
    assert shorturl_dict["owner"] == normal_shorturl.owner
    assert shorturl_dict["status"] == normal_shorturl.status
    assert shorturl_dict["visit_count"] == normal_shorturl.visit_count
    assert shorturl_dict["created_at"] == normal_shorturl.created_at
    assert shorturl_dict["expires_at"] == normal_shorturl.expires_at
    assert shorturl_dict["last_accessed_at"] == normal_shorturl.last_accessed_at


def test_to_domain(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    shorturl_dict = repository._to_dict(normal_shorturl)
    domain = repository._to_domain(shorturl_dict)
    assert domain.id == shorturl_dict["id"]
    assert domain.slug == shorturl_dict["slug"]
    assert domain.original_url == shorturl_dict["original_url"]
    assert domain.owner == shorturl_dict["owner"]
    assert domain.status == shorturl_dict["status"]
    assert domain.visit_count == shorturl_dict["visit_count"]
    assert domain.created_at == shorturl_dict["created_at"]
    assert domain.expires_at == shorturl_dict["expires_at"]
    assert domain.last_accessed_at == shorturl_dict["last_accessed_at"]


@pytest.mark.asyncio
async def test_add(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    retrieved = await repository.add(normal_shorturl)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug

    shorturl_dict = repository.data[1]
    assert shorturl_dict["id"] == 1
    assert shorturl_dict["slug"] == normal_shorturl.slug


@pytest.mark.asyncio
async def test_update(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    added = await repository.add(normal_shorturl)
    added.expires_at = None

    retrieved = await repository.update(added)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == added.id
    assert retrieved.expires_at == None


@pytest.mark.asyncio
async def test_get_all_with_no_shorturls(repository: MockShortURLRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_shorturls(
    repository: MockShortURLRepository, 
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
        assert retrieved[i].id == expected_id
    assert retrieved[0].slug == normal_shorturl.slug
    assert retrieved[1].slug == other_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_id(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    await repository.add(normal_shorturl)

    retrieved = await repository.get_by_id(1)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_slug(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    await repository.add(normal_shorturl)

    retrieved = await repository.get_by_slug(normal_shorturl.slug)

    assert isinstance(retrieved, ShortURL)
    assert retrieved.id == 1
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_list_paginated(
    repository: MockShortURLRepository, 
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
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    await repository.add(normal_shorturl)
    assert await repository.exists_by_slug(normal_shorturl.slug) is True


@pytest.mark.asyncio
async def test_exists_by_slug_false(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    assert await repository.exists_by_slug(normal_shorturl.slug) is False


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: MockShortURLRepository, normal_shorturl: ShortURL
):
    await repository.add(normal_shorturl) 

    deleted = await repository.delete_by_id(1)

    assert isinstance(deleted, ShortURL)
    assert deleted.id == 1
    assert deleted.slug == normal_shorturl.slug
    assert await repository.get_by_id(1) is None


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_shorturl(
    repository: MockShortURLRepository
):
    with pytest.raises(
        ShortURLNotFoundInDatabaseError,
        match=f"ShortURL with id=1 not found in MockShortURLRepository."
    ):
        await repository.delete_by_id(1)
