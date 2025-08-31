import pytest

from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.shorturl.exceptions import ShortURLAttributeTypeError
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl import ShortURL


def test_change_slug(normal_shorturl: ShortURL):
    new_slug = Slug("random")
    normal_shorturl.change_slug(new_slug)
    assert normal_shorturl.slug == new_slug


def test_change_slug_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_slug("a") # type: ignore


def test_change_original_url(normal_shorturl: ShortURL):
    new_original_url = URL("https://new.com")
    normal_shorturl.change_original_url(new_original_url)
    assert normal_shorturl.original_url == new_original_url


def test_change_original_url_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_original_url("a") # type: ignore


def test_change_owner_pk(normal_shorturl: ShortURL):
    new_owner_pk = PrimaryKey.create_pk_id(1)
    normal_shorturl.change_owner_pk(new_owner_pk)
    assert normal_shorturl.owner_pk == new_owner_pk


def test_change_owner_pk_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_owner_pk("a") # type: ignore

