import pytest

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import GeneralValidator
from shortener.domain.shorturl.rules.slug_length import (
    SLUG_MAX_LENGTH, SLUG_MIN_LENGTH
)
from shortener.domain.shorturl.exceptions import (
    ShortURLForbiddenSlugError, 
    ShortURLSlugAlreadyExistsError,
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError
)


@pytest.fixture
def validator(shorturl_general_validator) -> GeneralValidator:
    return shorturl_general_validator


@pytest.mark.asyncio
async def test_validate_valid_slug(validator: GeneralValidator):
    assert await validator._validate_slug("my-short-url") == None


@pytest.mark.asyncio
async def test_validate_forbidden_slug(validator: GeneralValidator):
    with pytest.raises(
        ShortURLForbiddenSlugError, match="The provided slug is forbidden."
    ):
        await validator._validate_slug("api")


@pytest.mark.asyncio
async def test_validate_longer_slug(validator: GeneralValidator):
    slug = "a" * (SLUG_MAX_LENGTH + 1)

    with pytest.raises(
        ShortURLSlugTooLongError, 
        match="The provided slug is longer than max length"
    ):
        await validator._validate_slug(slug)


@pytest.mark.asyncio
async def test_validate_slug_with_exactly_maxlength(validator: GeneralValidator):
    slug = "a" * SLUG_MAX_LENGTH 
    await validator._validate_slug(slug)


@pytest.mark.asyncio
async def test_validate_shorter_slug(validator: GeneralValidator):
    slug = "a" * (SLUG_MIN_LENGTH - 1)

    with pytest.raises(
        ShortURLSlugTooShortError, 
        match="The provided slug is shorter than min length"
    ):
        await validator._validate_slug(slug)


@pytest.mark.asyncio
async def test_validate_slug_with_exactly_min_length(validator: GeneralValidator):
    slug = "a" * SLUG_MIN_LENGTH
    await validator._validate_slug(slug)


@pytest.mark.asyncio
async def test_validate_already_exists_slug(
    validator: GeneralValidator, normal_shorturl: ShortURL
):
    await validator.repository.save(normal_shorturl)

    with pytest.raises(
        ShortURLSlugAlreadyExistsError, match="The provided slug already exists."
    ):
        await validator._validate_slug(normal_shorturl.slug)


@pytest.mark.asyncio
async def test_validate_valid_shorturl(
    validator: GeneralValidator, normal_shorturl: ShortURL
):
    assert await validator.validate(normal_shorturl) == None


@pytest.mark.asyncio
async def test_validate_invalid_shorturl(
    validator: GeneralValidator, normal_shorturl: ShortURL
):
    normal_shorturl.slug = "config"

    with pytest.raises(
        ShortURLForbiddenSlugError, match="The provided slug is forbidden."
    ):
        await validator.validate(normal_shorturl)
