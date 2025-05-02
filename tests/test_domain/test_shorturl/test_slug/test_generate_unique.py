import pytest

from tests.fixtures.mocks.shorturl_repository import MockShortURLRepository

from shortener.domain.shorturl.fields.slug import (
    Slug,
    DEFAULT_RANDOM_SLUG_LENGTH,
    DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG
)
from shortener.domain.shorturl.utils import generate_unique_slug


class SlugAlwaysExists(MockShortURLRepository):    
    async def exists_by_slug(self, slug: str) -> bool:
        return True


@pytest.fixture
def repository(mock_shorturl_repository):
    return mock_shorturl_repository


@pytest.mark.asyncio
async def test_raises_type_error_when_repository_is_missing():
    with pytest.raises(TypeError):
        await generate_unique_slug()


@pytest.mark.asyncio
async def test_return_type(repository: MockShortURLRepository):
    slug = await generate_unique_slug(repository=repository)
    assert isinstance(slug, Slug)


@pytest.mark.asyncio
async def test_default_length(repository: MockShortURLRepository):
    slug = await generate_unique_slug(repository=repository)
    assert len(slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_custom_length(repository: MockShortURLRepository):
    length = 10
    slug = await generate_unique_slug(repository=repository, length=length)
    assert len(slug) == length


@pytest.mark.asyncio
async def test_raises_runtime_error_when_max_attempts_reached():
    repository = SlugAlwaysExists()
    max_attempts = DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generate_unique_slug(repository=repository)


@pytest.mark.asyncio
async def test_raises_runtime_error_with_custom_max_attempts():
    repository = SlugAlwaysExists()
    max_attempts = 1

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generate_unique_slug(
            repository=repository, max_attempts=max_attempts
        )
