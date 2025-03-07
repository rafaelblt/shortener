import pytest

from datetime import datetime

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import GeneralValidator
from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError
from shortener.domain.shorturl.rules.slug_length import DEFAULT_RANDOM_SLUG_LENGTH

from shortener.use_cases import CreateShortURLUseCase


@pytest.fixture
def validator(mock_shorturl_repository):
    return GeneralValidator(mock_shorturl_repository)


@pytest.fixture
def use_case(mock_shorturl_repository, validator, shorturl_slug_generator):
    return CreateShortURLUseCase(
        repository=mock_shorturl_repository,
        validator=validator,
        slug_generator=shorturl_slug_generator
    )


@pytest.mark.asyncio
async def test_attrs_of_shorturl(use_case):
    shorturl = await use_case.execute(original_url="github.com")

    assert isinstance(shorturl, ShortURL)
    assert shorturl.original_url == "github.com"
    assert shorturl.owner_id == None
    assert shorturl.is_active
    assert len(shorturl.slug) == DEFAULT_RANDOM_SLUG_LENGTH
    assert isinstance(shorturl.created_at, datetime)
    assert shorturl.expires_at == None
    assert shorturl.last_accessed_at == None
    assert shorturl.visit_count == 0


@pytest.mark.asyncio
async def test_execute_with_full_args(use_case):
    shorturl = await use_case.execute(
        original_url="github.com",
        owner_id=1,
        custom_slug="git",
        expires_at=datetime(year=2038, month=5, day=21)
    )
    assert shorturl.owner_id == 1
    assert shorturl.slug == "git"
    assert isinstance(shorturl.expires_at, datetime)


@pytest.mark.asyncio
async def test_validation_raises_slug_already_exists(use_case):
    await use_case.execute(original_url="github.com", custom_slug="git")

    with pytest.raises(
        ShortURLSlugAlreadyExistsError, match="The provided slug already exists."
    ):
        await use_case.execute(original_url="gitlab.com", custom_slug="git")


@pytest.mark.asyncio
async def test_shorturl_is_saved_in_repository(use_case):
    await use_case.execute(original_url="github.com", custom_slug="git")
    assert await use_case.repository.exists_by_slug("git") is True
