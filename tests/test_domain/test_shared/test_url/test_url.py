import pytest

from shortener.domain.shared.valueobjects.url import URL, InvalidURLError


def test_new_url():
    url = URL("https://www.example.com")
    assert isinstance(url, URL)
    assert isinstance(url, URL)
    assert url == "https://www.example.com"


def test_new_url_with_invalid_value():
    value = "test-invalid"
    with pytest.raises(InvalidURLError) as e:
        URL(value)
    assert e.value.url == value


@pytest.mark.parametrize(
    "url, is_valid", 
    [
        ("https://www.google.com", True),
        ("https://example.com", True),
        ("http://www.google.com", True),
        ("ftp://example.com", True),
        ("invalid-url", False),
        ("https://", False),
        ("https://?", False),
    ]
)
def test_new_url_is_valid(url, is_valid):
    if is_valid:
        URL(url)
    else:
        with pytest.raises(InvalidURLError) as e:
            URL(url)
        assert e.value.url == url


@pytest.mark.parametrize(
    "url, is_https", 
    [
        ("https://www.google.com", True),
        ("https://example.com", True),
        ("http://www.google.com", False),
        ("ftp://example.com", False),
    ]
)
def test_url_is_https(url, is_https):
    assert URL(url).is_https() == is_https
