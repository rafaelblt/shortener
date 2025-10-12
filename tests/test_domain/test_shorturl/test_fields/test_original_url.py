import pytest

from shortener.domain.shared.valueobjects.url import URL
from shortener.domain.shorturl.fields.url import OriginalURL
from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


def test_new_original_url():
    url = OriginalURL("https://www.example.com")
    assert isinstance(url, OriginalURL)
    assert isinstance(url, URL)
    assert url == "https://www.example.com"


def test_new_original_url_with_invalid_value():
    value = "test-invalid"
    with pytest.raises(ShortURLInvalidURLError) as e:
        OriginalURL(value)
    assert e.value.url == value


@pytest.mark.parametrize(
    "url, is_valid", 
    [
        ("https://www.google.com", True),
        ("https://example.com", True),
        ("http://www.google.com", False),
        ("ftp://example.com", False),
        ("invalid-url", False),
        ("https://", False),
        ("https://?", False),
    ]
)
def test_url_is_valid(url, is_valid):
    if is_valid:
        OriginalURL(url)
    else:
        with pytest.raises(ShortURLInvalidURLError) as e:
            OriginalURL(url)
        assert e.value.url == url
