import pytest

from shortener.domain.shorturl.fields.url import URL
from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


def test_new_url():
    url = URL("https://www.example.com")
    assert isinstance(url, URL)
    assert isinstance(url, str)
    assert url == "https://www.example.com"


def test_new_url_with_invalid_value():
    value = "test-invalid"
    with pytest.raises(
        ShortURLInvalidURLError, match="URL must be a valid https url."
    ):
        URL(value)
