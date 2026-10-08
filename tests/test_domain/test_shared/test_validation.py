import re
import pytest

from shortener.domain.shared.result import Ok, Result
from shortener.domain.shared.validation import (
    IssueCode,
    StringValidation,
    ValidationError,
)
from tests.fixtures.domain.validation import invalid


LOWERCASE_LETTERS = re.compile(r"[a-z]+")


@pytest.mark.parametrize("value", [123, None, b"abc"])
def test_value_that_is_not_a_string_only_gets_invalid_type(value: object):
    result = (
        StringValidation(value)
        .min_length(10)
        .matches(LOWERCASE_LETTERS)
        .satisfies(lambda value: False, IssueCode.INVALID_FORMAT)
        .result()
    )
    assert result == invalid(IssueCode.INVALID_TYPE)


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("ab", invalid(IssueCode.TOO_SHORT), id="shorter"),
        pytest.param("abc", Ok("abc"), id="same length"),
        pytest.param("abcd", Ok("abcd"), id="longer"),
    ],
)
def test_min_length_records_too_short_only_for_a_shorter_value(
    value: str, expected: Result[str, ValidationError]
):
    assert StringValidation(value).min_length(3).result() == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("ab", Ok("ab"), id="shorter"),
        pytest.param("abc", Ok("abc"), id="same length"),
        pytest.param("abcd", invalid(IssueCode.TOO_LONG), id="longer"),
    ],
)
def test_max_length_records_too_long_only_for_a_longer_value(
    value: str, expected: Result[str, ValidationError]
):
    assert StringValidation(value).max_length(3).result() == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("abc", Ok("abc"), id="whole value"),
        pytest.param("abc!", invalid(IssueCode.INVALID_FORMAT), id="trailing character"),
        pytest.param("!abc", invalid(IssueCode.INVALID_FORMAT), id="leading character"),
        pytest.param("abc\n", invalid(IssueCode.INVALID_FORMAT), id="trailing newline"),
    ],
)
def test_matches_records_invalid_format_unless_the_whole_value_matches(
    value: str, expected: Result[str, ValidationError]
):
    assert StringValidation(value).matches(LOWERCASE_LETTERS).result() == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("abc", Ok("abc"), id="follows the rule"),
        pytest.param("ABC", invalid(IssueCode.INVALID_FORMAT), id="breaks the rule"),
    ],
)
def test_satisfies_records_the_given_code_only_when_the_rule_is_broken(
    value: str, expected: Result[str, ValidationError]
):
    validation = StringValidation(value).satisfies(str.islower, IssueCode.INVALID_FORMAT)
    assert validation.result() == expected


def test_records_an_issue_for_each_broken_rule_in_the_order_of_the_chain():
    result = (
        StringValidation("a!")
        .matches(LOWERCASE_LETTERS)
        .min_length(3)
        .max_length(1)
        .result()
    )
    assert result == invalid(
        IssueCode.INVALID_FORMAT, IssueCode.TOO_SHORT, IssueCode.TOO_LONG
    )
