import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError
from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.domain.user.exceptions import ShortURLLimitReachedError, UserNotFoundError
from shortener.domain.user import User
from shortener.use_cases import CreateShortURLForUserUseCase


@pytest.fixture
def use_case(mock_shorturl_repository, mock_user_repository):
    return CreateShortURLForUserUseCase(
        shorturl_repository=mock_shorturl_repository,
        user_repository=mock_user_repository,
    )


@pytest.mark.asyncio
async def test_instance_retrieved(
    use_case: CreateShortURLForUserUseCase,
    other_shorturl: ShortURL,
    poor_user: User,
):
    poor_user = await use_case.user_repo.add(poor_user)

    retrieved = await use_case.execute(
        original_url=other_shorturl.original_url,
        custom_slug=other_shorturl.slug,
        owner_pk=poor_user.pk
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
    poor_user = await use_case.user_repo.add(poor_user)
    shorturl = await use_case.execute(
        original_url=other_shorturl.original_url,
        owner_pk=poor_user.pk
    )
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(
    use_case: CreateShortURLForUserUseCase,
    normal_shorturl: ShortURL,
    poor_user: User,
):
    poor_user = await use_case.user_repo.add(poor_user)
    await use_case.execute(
        original_url=normal_shorturl.original_url,
        custom_slug=normal_shorturl.slug,
        owner_pk=poor_user.pk
    )
    assert await use_case.shorturl_repo.exists_by_slug(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_with_non_existent_user(
    use_case: CreateShortURLForUserUseCase,
    normal_shorturl: ShortURL,
    poor_user: User,
):
    poor_user._pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(UserNotFoundError) as e:
        await use_case.execute(
            original_url=normal_shorturl.original_url,
            custom_slug=normal_shorturl.slug,
            owner_pk=poor_user.pk
        )
    assert e.value.value == poor_user.pk
    assert e.value.field == "pk"


@pytest.mark.asyncio
async def test_with_slug_already_exists(
    use_case: CreateShortURLForUserUseCase,
    normal_shorturl: ShortURL,
    poor_user: User,
):
    poor_user = await use_case.user_repo.add(poor_user)
    await use_case.shorturl_repo.add(normal_shorturl)
    with pytest.raises(ShortURLSlugAlreadyExistsError) as e:
        await use_case.execute(
            original_url=normal_shorturl.original_url,
            custom_slug=normal_shorturl.slug,
            owner_pk=poor_user.pk
        )
    assert e.value.slug == normal_shorturl.slug


@pytest.mark.asyncio
async def test_shorturl_limit_reached_error(
    use_case: CreateShortURLForUserUseCase,
    normal_shorturl: ShortURL,
    poor_user: User,
):
    poor_user = await use_case.user_repo.add(poor_user)
    for _ in range(poor_user.plan.max_shorturls):
        await use_case.execute(
            original_url=normal_shorturl.original_url,
            owner_pk=poor_user.pk
        )
    with pytest.raises(ShortURLLimitReachedError) as e:
        await use_case.execute(
            original_url=normal_shorturl.original_url,
            owner_pk=poor_user.pk
        )
    assert e.value.max_shorturls == poor_user.plan.max_shorturls
