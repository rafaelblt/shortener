import pytest
import pytest_asyncio

from tests.fixtures.mocks import MockShortURLRepository

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import (
    ShortURLNotFoundInDatabaseError, ShortURLAvailabilityError
)

from shortener.use_cases import ResolveShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository: MockShortURLRepository):
    return ResolveShortURLUseCase(repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_resolve_slug(
    use_case: ResolveShortURLUseCase, normal_shorturl: ShortURL
):
    await use_case.repository.add(normal_shorturl)
    original_url = await use_case.resolve_slug(normal_shorturl.slug)
    assert original_url == normal_shorturl.original_url


@pytest.mark.asyncio
async def test_resolve_slug_raises_not_found(use_case: ResolveShortURLUseCase):
    with pytest.raises(ShortURLNotFoundInDatabaseError):
        await use_case.resolve_slug("non-existent-slug")


@pytest.mark.asyncio
async def test_resolve_slug_raises_availability_error(
    use_case: ResolveShortURLUseCase, expired_shorturl: ShortURL
):
    await use_case.repository.add(expired_shorturl)
    with pytest.raises(ShortURLAvailabilityError):
        await use_case.resolve_slug(expired_shorturl.slug)
