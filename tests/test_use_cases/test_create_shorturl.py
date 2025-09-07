import pytest

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.use_cases import CreateShortURLUseCase


@pytest.fixture
def use_case(mock_shorturl_repository):
    return CreateShortURLUseCase(shorturl_repository=mock_shorturl_repository)


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    retrieved = await use_case.execute(
        original_url=normal_shorturl.original_url,
        custom_slug=normal_shorturl.slug
    )
    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert retrieved.original_url == normal_shorturl.original_url
    assert retrieved.slug == normal_shorturl.slug
    assert retrieved.owner_pk.is_undefined()


@pytest.mark.asyncio
async def test_slug_generator(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    shorturl = await use_case.execute(
        original_url=normal_shorturl.original_url
    )
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    await use_case.execute(
        original_url=normal_shorturl.original_url,
        custom_slug=normal_shorturl.slug
    )
    assert await use_case.shorturl_repository.exists_by_slug(normal_shorturl.slug)
