import pytest

from shortener.domain.shared.validation import IssueCode
from shortener.domain.shorturl.slug import Slug
from tests.fixtures.domain.validation import invalid
from tests.utils.text_helpers import assert_mentions


def test_new_slug():
    slug = Slug("test")
    assert isinstance(slug, Slug)
    assert isinstance(slug, str)
    assert slug == "test"


def test_new_slug_with_invalid_value_raises_value_error_with_the_validation_error():
    with pytest.raises(ValueError) as raised:
        Slug("test.invalid")
    assert raised.value.args == (invalid(IssueCode.INVALID_FORMAT).error,)


def test_repr_mentions_the_class_and_the_value():
    assert_mentions(repr(Slug("test")), Slug.__name__, "test")
