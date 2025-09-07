import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.domain.user.user import User
from shortener.use_cases import CreateShortURLForUserUseCase


@pytest.fixture
def use_case(mock_shorturl_repository):
    return CreateShortURLForUserUseCase(
        shorturl_repository=mock_shorturl_repository
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateShortURLForUserUseCase,
    other_shorturl: ShortURL,
    poor_user: User,
):
    poor_user._pk = PrimaryKey.create_pk_id(1)

    retrieved = await use_case.execute(
        original_url=other_shorturl.original_url,
        custom_slug=other_shorturl.slug,
        owner=poor_user
    )

    assert isinstance(retrieved, ShortURL)
    assert retrieved.pk.get_id() == 1
    assert retrieved.original_url == other_shorturl.original_url
    assert retrieved.slug == other_shorturl.slug
    assert retrieved.owner_pk == poor_user.pk
    assert retrieved in await poor_user.get_shorturls()


@pytest.mark.asyncio
async def test_slug_generator(
    use_case: CreateShortURLForUserUseCase,
    other_shorturl: ShortURL,
    poor_user: User
):
    shorturl = await use_case.execute(
        original_url=other_shorturl.original_url,
        owner=poor_user
    )
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(
    use_case: CreateShortURLForUserUseCase,
    normal_shorturl: ShortURL,
    poor_user: User,
):
    await use_case.execute(
        original_url=normal_shorturl.original_url,
        custom_slug=normal_shorturl.slug,
        owner=poor_user
    )
    assert await use_case.shorturl_repository.exists_by_slug(normal_shorturl.slug)
