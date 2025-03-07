import pytest

from tests.mocks import MockShortURLRepository

from shortener.domain.shorturl import SlugGenerator


class ExistOnlyTrueRepo(MockShortURLRepository):    
    async def exists_by_slug(self, slug: str) -> bool:
        return True


@pytest.fixture
def generator(shorturl_slug_generator) -> SlugGenerator:
    return shorturl_slug_generator


@pytest.fixture
def repository(mock_shorturl_repository):
    return mock_shorturl_repository


@pytest.mark.asyncio
async def test_raises_type_error_when_repository_is_missing(generator: SlugGenerator):
    with pytest.raises(TypeError):
        await generator.generate_unique_slug()


@pytest.mark.asyncio
async def test_return_type(generator: SlugGenerator, repository: MockShortURLRepository):
    slug = await generator.generate_unique_slug(repository=repository)
    assert isinstance(slug, str)


@pytest.mark.asyncio
async def test_default_length(generator: SlugGenerator, repository: MockShortURLRepository):
    slug = await generator.generate_unique_slug(repository=repository)
    assert len(slug) == 6


@pytest.mark.asyncio
async def test_custom_length(generator: SlugGenerator, repository: MockShortURLRepository):
    slug = await generator.generate_unique_slug(repository=repository, length=10)
    assert len(slug) == 10


@pytest.mark.asyncio
async def test_raises_runtime_error_when_max_attempts_reached(generator: SlugGenerator):
    repository = ExistOnlyTrueRepo()
    max_attempts = 100

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generator.generate_unique_slug(repository=repository)


@pytest.mark.asyncio
async def test_raises_runtime_error_with_custom_max_attempts(generator: SlugGenerator):
    repository = ExistOnlyTrueRepo()
    max_attempts = 1

    with pytest.raises(
        RuntimeError, 
        match=f"Could not generate a unique slug after {max_attempts} attempts."
    ):
        await generator.generate_unique_slug(
            repository=repository, max_attempts=max_attempts
        )
