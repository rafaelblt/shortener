import pytest

from pydantic import ValidationError

from shortener.adapters.api.v1.schemas.payloads.shorturl import CreateShortURLPayload
from shortener.domain.shorturl.fields import OriginalURL, Slug


@pytest.fixture
def valid_original_url(normal_shorturl):
    return normal_shorturl.original_url.__str__()


@pytest.fixture
def valid_custom_slug(normal_shorturl):
    return normal_shorturl.slug.__str__()


def test_blank_data():
    with pytest.raises(ValidationError) as exc:
        CreateShortURLPayload() # type: ignore
    assert len(exc.value.errors()) == 1


def test_without_custom_slug(valid_original_url):
    payload = CreateShortURLPayload(original_url=valid_original_url)
    assert payload.original_url == valid_original_url
    assert payload.custom_slug == None


def test_full_data(valid_original_url, valid_custom_slug):
    payload = CreateShortURLPayload(
        original_url=valid_original_url, custom_slug=valid_custom_slug
    )
    assert payload.original_url == valid_original_url
    assert payload.custom_slug == valid_custom_slug


def test_convert_original_url(valid_original_url, valid_custom_slug):
    payload = CreateShortURLPayload(
        original_url=valid_original_url, custom_slug=valid_custom_slug
    )
    retrieved = payload.convert_original_url()
    assert isinstance(retrieved, OriginalURL)
    assert retrieved == valid_original_url


def test_convert_custom_slug(valid_original_url, valid_custom_slug):
    payload = CreateShortURLPayload(
        original_url=valid_original_url, custom_slug=valid_custom_slug
    )
    retrieved = payload.convert_custom_slug()
    assert isinstance(retrieved, Slug)
    assert retrieved == valid_custom_slug


def test_convert_none_custom_slug(valid_original_url):
    payload = CreateShortURLPayload(
        original_url=valid_original_url, custom_slug=None
    )
    retrieved = payload.convert_custom_slug()
    assert retrieved == None
