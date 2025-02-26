from pytest import fixture

from .mocks import MockShortURLRepository

from shortener.domain.shorturl import ShortURL, SlugGenerator
from shortener.domain.shorturl.validators import (
    AvailabilityValidator as ShortURLAvailabilityValidator,
    GeneralValidator as ShortURLGeneralValidator
)


@fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@fixture
def shorturl_slug_generator():
    return SlugGenerator()


@fixture
def normal_shorturl():
    return ShortURL(
        slug="lorem-ipsum-website",
        original_url="lorem.makeyoursite.com"
    )


@fixture
def shorturl_availability_validator():
    return ShortURLAvailabilityValidator()
