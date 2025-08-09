import pytest

from shortener.domain.shorturl import ShortURL, ShortURLValidator
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.use_cases import CreateShortURLUseCase


class MockValidator(ShortURLValidator):
    async def validate(self, shorturl: ShortURL):
        if shorturl.slug == "joker":
            raise ValueError("The provided slug is joker.")


@pytest.fixture
def use_case(mock_shorturl_repository, mock_user_repository):
    return CreateShortURLUseCase(
        shorturl_repository=mock_shorturl_repository,
        user_repository=mock_user_repository,
        validator=MockValidator(),
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    owner = await use_case.user_repository.add(normal_shorturl.owner)
    retrieved = await use_case.execute(
        original_url=normal_shorturl.original_url,
        owner_id=owner.id,
        custom_slug=normal_shorturl.slug
    )
    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert retrieved.original_url == normal_shorturl.original_url
    assert retrieved.owner.id == owner.id
    assert retrieved.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_slug_generated(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    owner = await use_case.user_repository.add(normal_shorturl.owner)
    shorturl = await use_case.execute(
        original_url=normal_shorturl.original_url, owner_id=owner.id
    )
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    owner = await use_case.user_repository.add(normal_shorturl.owner)
    await use_case.execute(
        original_url=normal_shorturl.original_url,
        custom_slug=normal_shorturl.slug,
        owner_id=owner.id
    )
    assert await use_case.shorturl_repository.exists_by_slug(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_shorturl_validation_is_called(
    use_case: CreateShortURLUseCase, normal_shorturl: ShortURL
):
    owner = await use_case.user_repository.add(normal_shorturl.owner)
    with pytest.raises(ValueError, match="The provided slug is joker."):
        await use_case.execute(
            original_url=normal_shorturl.original_url,
            owner_id=owner.id,
            custom_slug=Slug("joker")
        )
