import pytest
import pytest_asyncio

from shortener.domain.shorturl import ShortURL
from shortener.use_cases import GetShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository):
    return GetShortURLUseCase(repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_get_by_id(
    use_case: GetShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.repository.add(normal_shorturl)
    retrieved = await use_case.get_by_id(shorturl.id)
    assert isinstance(retrieved, ShortURL)
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_id_non_existent(use_case: GetShortURLUseCase):
    retrieved = await use_case.get_by_id(14514352)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_slug(
    use_case: GetShortURLUseCase, normal_shorturl: ShortURL
):
    await use_case.repository.add(normal_shorturl)
    retrieved = await use_case.get_by_slug(normal_shorturl.slug)
    assert isinstance(retrieved, ShortURL)
    assert retrieved.original_url == normal_shorturl.original_url


@pytest.mark.asyncio
async def test_get_by_slug_non_existent(use_case: GetShortURLUseCase):
    retrieved = await use_case.get_by_slug("non-existent-slug")
    assert retrieved is None
