import pytest
import pytest_asyncio
import copy

from shortener.domain.shorturl import ShortURL
from shortener.use_cases import GetShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository, normal_shorturl):
    repository = copy.deepcopy(mock_shorturl_repository)
    await repository.save(normal_shorturl)
    return GetShortURLUseCase(repository=repository)


@pytest.mark.asyncio
async def test_get_by_id(
    use_case: GetShortURLUseCase, normal_shorturl: ShortURL
):
    retrieved = await use_case.get_by_id(1)
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_id_non_existent(use_case: GetShortURLUseCase):
    retrieved = await use_case.get_by_id(2)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_slug(use_case, normal_shorturl):
    retrieved = await use_case.get_by_slug(normal_shorturl.slug)
    assert retrieved.original_url == normal_shorturl.original_url


@pytest.mark.asyncio
async def test_get_by_slug_non_existent(use_case):
    retrieved = await use_case.get_by_slug("non-existent-slug")
    assert retrieved is None
