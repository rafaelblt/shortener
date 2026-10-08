import pytest

from shortener.domain.shared.result import Ok
from shortener.domain.shared.validation import IssueCode
from shortener.domain.shorturl.target_url import TargetURL
from tests.fixtures.domain.validation import invalid
from tests.utils.text_helpers import assert_mentions


def test_create_returns_ok_with_the_value():
    value = "https://www.example.com/path?query=1"
    assert TargetURL.create(value) == Ok(value)


def test_the_value_in_ok_is_a_target_url():
    assert isinstance(TargetURL.create("https://example.com").unwrap(), TargetURL)


def test_create_accepts_an_uppercase_scheme():
    assert TargetURL.create("HTTPS://example.com") == Ok("HTTPS://example.com")


@pytest.mark.parametrize(
    "value",
    ["http://example.com", "ftp://example.com", "example.com", ""],
)
def test_create_without_https_scheme_is_an_invalid_format(value):
    assert TargetURL.create(value) == invalid(IssueCode.INVALID_FORMAT)


@pytest.mark.parametrize("value", ["https://", "https://?", "https:///path"])
def test_create_without_host_is_an_invalid_format(value):
    assert TargetURL.create(value) == invalid(IssueCode.INVALID_FORMAT)


def test_create_with_a_value_that_cannot_be_parsed_is_an_invalid_format():
    assert TargetURL.create("https://[invalid") == invalid(IssueCode.INVALID_FORMAT)


@pytest.mark.parametrize("value", [123, None])
def test_create_with_a_value_that_is_not_a_string_is_an_invalid_type(value):
    assert TargetURL.create(value) == invalid(IssueCode.INVALID_TYPE)


def test_new_target_url():
    target_url = TargetURL("https://www.example.com/path?query=1")
    assert isinstance(target_url, TargetURL)
    assert isinstance(target_url, str)
    assert target_url == "https://www.example.com/path?query=1"


def test_new_target_url_with_invalid_value_raises_value_error_with_the_validation_error():
    with pytest.raises(ValueError) as raised:
        TargetURL("http://example.com")
    assert raised.value.args == (invalid(IssueCode.INVALID_FORMAT).error,)


def test_parse_returns_a_target_url_with_the_value():
    target_url = TargetURL.parse("https://example.com")
    assert isinstance(target_url, TargetURL)
    assert target_url == "https://example.com"


@pytest.mark.parametrize("value", ["http://example.com", "https://"])
def test_parse_accepts_a_value_that_breaks_the_rules_of_create(value):
    assert TargetURL.parse(value) == value


@pytest.mark.parametrize("value", [123, None])
def test_parse_rejects_a_value_that_is_not_a_string_with_type_error(value):
    with pytest.raises(TypeError) as raised:
        TargetURL.parse(value)
    assert_mentions(str(raised.value), TargetURL.__name__)


def test_parse_rejects_an_empty_string_with_value_error():
    with pytest.raises(ValueError) as raised:
        TargetURL.parse("")
    assert_mentions(str(raised.value), TargetURL.__name__)


def test_repr_mentions_the_class_and_the_value():
    value = "https://example.com"
    assert_mentions(repr(TargetURL(value)), TargetURL.__name__, value)
