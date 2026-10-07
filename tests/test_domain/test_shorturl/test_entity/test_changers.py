import pytest

from shortener.domain.shorturl.exceptions import ShortURLAttributeTypeError
from shortener.domain.shorturl import Slug, TargetURL
from shortener.domain.shorturl import ShortURL


def test_change_slug(normal_shorturl: ShortURL):
    new_slug = Slug("random")
    normal_shorturl.change_slug(new_slug)
    assert normal_shorturl.slug == new_slug


def test_change_slug_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_slug("a") # type: ignore


def test_change_target_url(normal_shorturl: ShortURL):
    new_target_url = TargetURL("https://new.com")
    normal_shorturl.change_target_url(new_target_url)
    assert normal_shorturl.target_url == new_target_url


def test_change_target_url_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_target_url("a") # type: ignore

