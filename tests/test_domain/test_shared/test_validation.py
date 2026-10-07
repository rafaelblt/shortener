import re
import pytest

from shortener.domain.shared.result import Ok
from shortener.domain.shared.validation import IssueCode, StringValidation
from tests.fixtures.domain.validation import invalid


LOWERCASE_LETTERS = re.compile(r"[a-z]+")


def test_result_is_ok_with_the_value_when_no_rule_is_broken():
    assert StringValidation("abc").min_length(3).max_length(3).result() == Ok("abc")


@pytest.mark.parametrize("value", [123, None, b"abc"])
def test_value_that_is_not_a_string_only_gets_invalid_type(value):
    result = (
        StringValidation(value)
        .min_length(10)
        .matches(LOWERCASE_LETTERS)
        .satisfies(lambda value: False, IssueCode.INVALID_FORMAT)
        .result()
    )
    assert result == invalid(IssueCode.INVALID_TYPE)


def test_min_length_accepts_a_value_with_exactly_the_length():
    assert StringValidation("abc").min_length(3).result() == Ok("abc")


def test_min_length_rejects_a_shorter_value_as_too_short():
    assert StringValidation("ab").min_length(3).result() == invalid(IssueCode.TOO_SHORT)


def test_max_length_accepts_a_value_with_exactly_the_length():
    assert StringValidation("abc").max_length(3).result() == Ok("abc")


def test_max_length_rejects_a_longer_value_as_too_long():
    assert StringValidation("abcd").max_length(3).result() == invalid(IssueCode.TOO_LONG)


def test_matches_accepts_a_value_that_matches_the_pattern():
    assert StringValidation("abc").matches(LOWERCASE_LETTERS).result() == Ok("abc")


@pytest.mark.parametrize("value", ["abc!", "!abc", "abc\n"])
def test_matches_rejects_a_value_that_only_partially_matches_as_invalid_format(value):
    result = StringValidation(value).matches(LOWERCASE_LETTERS).result()
    assert result == invalid(IssueCode.INVALID_FORMAT)


def test_satisfies_accepts_a_value_that_follows_the_rule():
    result = StringValidation("abc").satisfies(str.islower, IssueCode.INVALID_FORMAT).result()
    assert result == Ok("abc")


def test_satisfies_rejects_a_value_that_breaks_the_rule_with_the_given_code():
    result = StringValidation("ABC").satisfies(str.islower, IssueCode.INVALID_FORMAT).result()
    assert result == invalid(IssueCode.INVALID_FORMAT)


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
