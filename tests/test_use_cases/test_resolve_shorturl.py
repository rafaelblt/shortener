import copy

import pytest
import pytest_asyncio

from tests.mocks import MockShortURLRepository

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import (
    ShortURLNotFoundInDatabase, ShortURLAvailabilityError
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
    with pytest.raises(ShortURLNotFoundInDatabase):
        await use_case.resolve_slug("non-existent-slug")


@pytest.mark.asyncio
async def test_resolve_slug_raises_availability_error(
    use_case: ResolveShortURLUseCase, expired_shorturl: ShortURL
):
    await use_case.repository.add(expired_shorturl)
    with pytest.raises(ShortURLAvailabilityError):
        await use_case.resolve_slug(expired_shorturl.slug)
