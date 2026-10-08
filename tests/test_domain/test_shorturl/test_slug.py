import pytest

from shortener.domain.shared.result import Ok
from shortener.domain.shared.validation import IssueCode
from shortener.domain.shorturl.slug import (
    Slug,
    RANDOM_SLUG_CHARS,
    RANDOM_SLUG_LENGTH,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH,
    SLUG_PATTERN,
)
from tests.fixtures.domain.validation import invalid
from tests.utils.text_helpers import assert_mentions


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("My-slug_1", id="letters, digits, - and _"),
        pytest.param("a" * SLUG_MIN_LENGTH, id="minimum length"),
        pytest.param("a" * SLUG_MAX_LENGTH, id="maximum length"),
    ],
)
def test_create_returns_ok_with_a_slug_of_a_valid_value(value: str):
    result = Slug.create(value)
    assert result == Ok(value)
    assert isinstance(result.unwrap(), Slug)


@pytest.mark.parametrize(
    "value, codes",
    [
        pytest.param("a" * (SLUG_MIN_LENGTH - 1), [IssueCode.TOO_SHORT], id="too short"),
        pytest.param("a" * (SLUG_MAX_LENGTH + 1), [IssueCode.TOO_LONG], id="too long"),
        pytest.param("dot.slug", [IssueCode.INVALID_FORMAT], id="dot"),
        pytest.param("with space", [IssueCode.INVALID_FORMAT], id="space"),
        pytest.param("acentuação", [IssueCode.INVALID_FORMAT], id="non-ascii letters"),
        pytest.param("abc\n", [IssueCode.INVALID_FORMAT], id="trailing newline"),
        pytest.param("", [IssueCode.INVALID_FORMAT, IssueCode.TOO_SHORT], id="empty"),
        pytest.param(
            "." * (SLUG_MAX_LENGTH + 1),
            [IssueCode.INVALID_FORMAT, IssueCode.TOO_LONG],
            id="too long with dots",
        ),
        pytest.param(12345, [IssueCode.INVALID_TYPE], id="int"),
        pytest.param(None, [IssueCode.INVALID_TYPE], id="None"),
    ],
)
def test_create_returns_err_with_an_issue_for_each_broken_rule(
    value: object, codes: list[IssueCode]
):
    assert Slug.create(value) == invalid(*codes)


def test_constructor_returns_a_slug_with_the_value():
    slug = Slug("my-slug")
    assert isinstance(slug, Slug)
    assert slug == "my-slug"


def test_constructor_raises_value_error_with_the_validation_error():
    with pytest.raises(ValueError) as raised:
        Slug("dot.slug")
    assert raised.value.args == (invalid(IssueCode.INVALID_FORMAT).error,)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("my-slug", id="valid"),
        pytest.param("a", id="too short"),
        pytest.param("a" * (SLUG_MAX_LENGTH + 1), id="too long"),
        pytest.param("dot.slug", id="invalid format"),
    ],
)
def test_parse_returns_a_slug_of_any_non_empty_string(value: str):
    slug = Slug.parse(value)
    assert isinstance(slug, Slug)
    assert slug == value


@pytest.mark.parametrize(
    "value, error",
    [
        pytest.param(12345, TypeError, id="int"),
        pytest.param(None, TypeError, id="None"),
        pytest.param("", ValueError, id="empty"),
    ],
)
def test_parse_rejects_an_empty_string_or_a_value_that_is_not_a_string(
    value: object, error: type[Exception]
):
    with pytest.raises(error) as raised:
        Slug.parse(value)
    assert_mentions(str(raised.value), Slug.__name__)


def test_generate_returns_a_slug_of_random_slug_chars_and_length():
    slug = Slug.generate()
    assert isinstance(slug, Slug)
    assert len(slug) == RANDOM_SLUG_LENGTH
    assert set(slug) <= set(RANDOM_SLUG_CHARS)


def test_generate_never_breaks_the_rules_of_create():
    # Covers every slug generate() can return, not just the one it returns now.
    assert SLUG_MIN_LENGTH <= RANDOM_SLUG_LENGTH <= SLUG_MAX_LENGTH
    assert SLUG_PATTERN.fullmatch(RANDOM_SLUG_CHARS)


def test_repr_mentions_the_class_and_the_value():
    value = "my-slug"
    assert_mentions(repr(Slug(value)), Slug.__name__, value)
