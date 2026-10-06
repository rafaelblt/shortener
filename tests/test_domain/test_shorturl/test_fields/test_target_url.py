import pytest

from shortener.domain.shorturl.fields.target_url import TargetURL
from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


def test_new_target_url():
    target_url = TargetURL("https://www.example.com/path?query=1")
    assert isinstance(target_url, TargetURL)
    assert isinstance(target_url, str)
    assert target_url == "https://www.example.com/path?query=1"


def test_new_target_url_with_uppercase_scheme():
    assert TargetURL("HTTPS://example.com") == "HTTPS://example.com"


@pytest.mark.parametrize(
    "value",
    ["http://example.com", "ftp://example.com", "example.com", ""],
)
def test_new_target_url_without_https_scheme_raises_error(value):
    with pytest.raises(ShortURLInvalidURLError) as e:
        TargetURL(value)
    assert e.value.url == value


@pytest.mark.parametrize("value", ["https://", "https://?", "https:///path"])
def test_new_target_url_without_host_raises_error(value):
    with pytest.raises(ShortURLInvalidURLError) as e:
        TargetURL(value)
    assert e.value.url == value


def test_new_target_url_that_cannot_be_parsed_raises_error():
    value = "https://[invalid"
    with pytest.raises(ShortURLInvalidURLError) as e:
        TargetURL(value)
    assert e.value.url == value


def test_validate_target_url_returns_none_for_valid_value():
    assert TargetURL.validate_target_url("https://example.com") is None


def test_validate_target_url_raises_error_for_invalid_value():
    with pytest.raises(ShortURLInvalidURLError):
        TargetURL.validate_target_url("http://example.com")


def test_target_url_repr():
    assert repr(TargetURL("https://example.com")) == "<TargetURL('https://example.com')>"
