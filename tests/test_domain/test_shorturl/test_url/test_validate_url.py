import pytest

from shortener.domain.shorturl.url import URL
from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


def test_valid_url():
    valid_url = "https://www.example.com"
    assert URL.validate_url(valid_url) is None
    

def test_invalid_url():
    invalid_url = "invalid-url"
    with pytest.raises(
        ShortURLInvalidURLError, match="URL must be a valid https url."
    ):
        URL.validate_url(invalid_url)
