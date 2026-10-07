import pytest

from shortener.domain.shared.validation import IssueCode
from shortener.domain.shorturl.slug import Slug
from tests.fixtures.domain.validation import invalid


def test_new_slug():
    slug = Slug("test")
    assert isinstance(slug, Slug)
    assert isinstance(slug, str)
    assert slug == "test"


def test_new_slug_with_invalid_value_raises_value_error_with_the_validation_error():
    with pytest.raises(ValueError) as raised:
        Slug("test.invalid")
    assert raised.value.args == (invalid(IssueCode.INVALID_FORMAT).error,)


def test_slug_repr():
    assert repr(Slug("test")) == "<Slug('test')>"
