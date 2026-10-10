import pytest

from shortener.shared.result import Ok
from shortener.shared.validation import IssueCode
from shortener.domain.target_url import TargetURL
from tests.fixtures.shared.validation import invalid
from tests.utils.text_helpers import assert_mentions


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("https://www.example.com/path?query=1", id="path and query"),
        pytest.param("HTTPS://example.com", id="uppercase scheme"),
    ],
)
def test_create_returns_ok_with_a_target_url_of_a_valid_value(value: str):
    result = TargetURL.create(value)
    assert result == Ok(value)
    assert isinstance(result.unwrap(), TargetURL)


@pytest.mark.parametrize(
    "value, codes",
    [
        pytest.param("http://example.com", [IssueCode.INVALID_FORMAT], id="http"),
        pytest.param("ftp://example.com", [IssueCode.INVALID_FORMAT], id="ftp"),
        pytest.param("example.com", [IssueCode.INVALID_FORMAT], id="no scheme"),
        pytest.param("", [IssueCode.INVALID_FORMAT], id="empty"),
        pytest.param("https://", [IssueCode.INVALID_FORMAT], id="no host"),
        pytest.param("https://?", [IssueCode.INVALID_FORMAT], id="query without host"),
        pytest.param("https:///path", [IssueCode.INVALID_FORMAT], id="path without host"),
        pytest.param("https://[invalid", [IssueCode.INVALID_FORMAT], id="unparsable"),
        pytest.param(123, [IssueCode.INVALID_TYPE], id="int"),
        pytest.param(None, [IssueCode.INVALID_TYPE], id="None"),
    ],
)
def test_create_returns_err_with_an_issue_for_each_broken_rule(
    value: object, codes: list[IssueCode]
):
    assert TargetURL.create(value) == invalid(*codes)


def test_constructor_returns_a_target_url_with_the_value():
    target_url = TargetURL("https://example.com")
    assert isinstance(target_url, TargetURL)
    assert target_url == "https://example.com"


def test_constructor_raises_value_error_with_the_validation_error():
    with pytest.raises(ValueError) as raised:
        TargetURL("http://example.com")
    assert raised.value.args == (invalid(IssueCode.INVALID_FORMAT).error,)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("https://example.com", id="valid"),
        pytest.param("http://example.com", id="http"),
        pytest.param("https://", id="no host"),
    ],
)
def test_parse_returns_a_target_url_of_any_non_empty_string(value: str):
    target_url = TargetURL.parse(value)
    assert isinstance(target_url, TargetURL)
    assert target_url == value


@pytest.mark.parametrize(
    "value, error",
    [
        pytest.param(123, TypeError, id="int"),
        pytest.param(None, TypeError, id="None"),
        pytest.param("", ValueError, id="empty"),
    ],
)
def test_parse_rejects_an_empty_string_or_a_value_that_is_not_a_string(
    value: object, error: type[Exception]
):
    with pytest.raises(error) as raised:
        TargetURL.parse(value)
    assert_mentions(str(raised.value), TargetURL.__name__)


def test_repr_mentions_the_class_and_the_value():
    value = "https://example.com"
    assert_mentions(repr(TargetURL(value)), TargetURL.__name__, value)
