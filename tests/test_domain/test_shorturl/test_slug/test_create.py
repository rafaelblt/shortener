import pytest

from shortener.domain.shared.result import Ok
from shortener.domain.shared.validation import IssueCode
from shortener.domain.shorturl.fields.slug import (
    Slug,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH
)
from tests.fixtures.domain.validation import invalid


def test_returns_ok_with_the_value():
    assert Slug.create("my-slug_1") == Ok("my-slug_1")


def test_the_value_in_ok_is_a_slug():
    assert isinstance(Slug.create("my-slug_1").unwrap(), Slug)


def test_accepts_the_minimum_length():
    value = "a" * SLUG_MIN_LENGTH
    assert Slug.create(value) == Ok(value)


def test_accepts_the_maximum_length():
    value = "a" * SLUG_MAX_LENGTH
    assert Slug.create(value) == Ok(value)


def test_shorter_than_the_minimum_length_is_too_short():
    value = "a" * (SLUG_MIN_LENGTH - 1)
    assert Slug.create(value) == invalid(IssueCode.TOO_SHORT)


def test_longer_than_the_maximum_length_is_too_long():
    value = "a" * (SLUG_MAX_LENGTH + 1)
    assert Slug.create(value) == invalid(IssueCode.TOO_LONG)


@pytest.mark.parametrize("value", ["dot.slug", "with space", "acentuação"])
def test_characters_outside_the_pattern_are_an_invalid_format(value):
    assert Slug.create(value) == invalid(IssueCode.INVALID_FORMAT)


def test_trailing_newline_is_an_invalid_format():
    assert Slug.create("abc\n") == invalid(IssueCode.INVALID_FORMAT)


@pytest.mark.parametrize("value", ["docs", "DOCS", "LogOut"])
def test_forbidden_slug_in_any_letter_case_is_forbidden(value):
    assert Slug.create(value) == invalid(IssueCode.FORBIDDEN)


def test_empty_value_is_an_invalid_format_and_too_short():
    assert Slug.create("") == invalid(IssueCode.INVALID_FORMAT, IssueCode.TOO_SHORT)


def test_reports_every_broken_rule():
    value = "." * (SLUG_MAX_LENGTH + 1)
    assert Slug.create(value) == invalid(IssueCode.INVALID_FORMAT, IssueCode.TOO_LONG)


@pytest.mark.parametrize("value", [12345, None])
def test_value_that_is_not_a_string_is_an_invalid_type(value):
    assert Slug.create(value) == invalid(IssueCode.INVALID_TYPE)
