import pytest
from shortener.domain.shorturl.fields.url import URL


@pytest.mark.parametrize(
    "url, expected", 
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
def test_is_valid_https_url(url, expected):
    assert URL.is_valid_https_url(url) == expected
