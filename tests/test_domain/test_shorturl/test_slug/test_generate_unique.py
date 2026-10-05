import pytest

from unittest.mock import AsyncMock, Mock

from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.shorturl.fields.slug import (
    Slug,
    DEFAULT_RANDOM_SLUG_LENGTH,
    DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG
)
from shortener.domain.shorturl.utils import generate_unique_slug


@pytest.fixture
def repository():
    repository = Mock(spec=ShortURLRepository)
    repository.exists_by_slug = AsyncMock(return_value=False)
    return repository


@pytest.fixture
def slug_always_exists_repo(repository):
    repository.exists_by_slug = AsyncMock(return_value=True)
    return repository


@pytest.mark.asyncio
async def test_return_type(repository: ShortURLRepository):
    slug = await generate_unique_slug(repository=repository)
    assert isinstance(slug, Slug)


@pytest.mark.asyncio
async def test_default_length(repository: ShortURLRepository):
    slug = await generate_unique_slug(repository=repository)
    assert len(slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_custom_length(repository: ShortURLRepository):
    length = 10
    slug = await generate_unique_slug(repository=repository, length=length)
    assert len(slug) == length


@pytest.mark.asyncio
async def test_raises_runtime_error_when_max_attempts_reached(slug_always_exists_repo):
    max_attempts = DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generate_unique_slug(repository=slug_always_exists_repo)


@pytest.mark.asyncio
async def test_raises_runtime_error_with_custom_max_attempts(slug_always_exists_repo):
    max_attempts = 1

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generate_unique_slug(
            repository=slug_always_exists_repo, max_attempts=max_attempts
        )
