import pytest

from shortener.domain.shorturl import ShortURL, ShortURLValidator
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.use_cases import CreateShortURLUseCase


class Validator(ShortURLValidator):
    async def validate(self, shorturl: ShortURL):
        if shorturl.slug == "joker":
            raise ValueError("The provided slug is joker.")


@pytest.fixture
def use_case(mock_shorturl_repository):
    return CreateShortURLUseCase(
        repository=mock_shorturl_repository,
        validator=Validator(),
    )

@pytest.fixture
def slug(normal_shorturl):
    return normal_shorturl.slug

@pytest.fixture
def url(normal_shorturl):
    return normal_shorturl.original_url


@pytest.mark.asyncio
async def test_instance_retrieved(use_case: CreateShortURLUseCase, url: URL):
    retrieved = await use_case.execute(original_url=url)
    assert isinstance(retrieved, ShortURL)


@pytest.mark.asyncio
async def test_original_url(use_case: CreateShortURLUseCase, url: URL):
    shorturl = await use_case.execute(original_url=url)
    assert shorturl.original_url == url


@pytest.mark.asyncio
async def test_slug_generated(use_case: CreateShortURLUseCase, url: URL):
    shorturl = await use_case.execute(original_url=url)
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_custom_slug(use_case: CreateShortURLUseCase, url: URL, slug: Slug):
    shorturl = await use_case.execute(original_url=url, custom_slug=slug)
    assert shorturl.slug == slug


@pytest.mark.asyncio
async def test_owner(use_case: CreateShortURLUseCase, url: URL, normal_user):
    owner = normal_user
    shorturl = await use_case.execute(original_url=url, owner=owner)
    assert shorturl.owner == owner


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(
    use_case: CreateShortURLUseCase, url: URL, slug: Slug
):
    await use_case.execute(original_url=url, custom_slug=slug)
    assert await use_case.repository.exists_by_slug(slug) is True


@pytest.mark.asyncio
async def test_validation_is_called(use_case: CreateShortURLUseCase, url: URL):
    with pytest.raises(ValueError, match="The provided slug is joker."):
        await use_case.execute(original_url=url, custom_slug=Slug("joker"))
