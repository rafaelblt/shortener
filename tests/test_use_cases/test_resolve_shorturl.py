import copy

import pytest
import pytest_asyncio

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import AvailabilityValidator
from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)

from shortener.use_cases import ResolveShortURLUseCase


@pytest_asyncio.fixture
async def use_case(mock_shorturl_repository, normal_shorturl):
    repository = copy.deepcopy(mock_shorturl_repository)
    validator = AvailabilityValidator()
    await repository.save(normal_shorturl)
    return ResolveShortURLUseCase(repository=repository, validator=validator)


@pytest.mark.asyncio
async def test_resolve_slug_with_nonexistent_slug(use_case: ResolveShortURLUseCase):
    original_url = await use_case.resolve_slug("nonexistent-slug")
    assert original_url is None


@pytest.mark.asyncio
async def test_resolve_slug_with_normal_shorturl(
    use_case: ResolveShortURLUseCase, normal_shorturl: ShortURL
):
    original_url = await use_case.resolve_slug(normal_shorturl.slug)
    assert original_url == normal_shorturl.original_url


@pytest.mark.asyncio
async def test_resolve_slug_raises_shorturl_inactive(
    use_case: ResolveShortURLUseCase, normal_shorturl: ShortURL
):
    use_case.repository.data[1]["is_active"] = False
    with pytest.raises(ShortURLInactiveError, match="The ShortURL is not active"):
        await use_case.resolve_slug(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_resolve_slug_raises_shorturl_expired(
    use_case: ResolveShortURLUseCase, normal_shorturl: ShortURL
):
    expire_datetime = use_case.repository.data[1]["created_at"]
    use_case.repository.data[1]["expires_at"] = expire_datetime
    with pytest.raises(ShortURLExpiredError, match="The ShortURL has expired"):
        await use_case.resolve_slug(normal_shorturl.slug)
