import pytest

from uuid import UUID

from shortener.domain.shorturl.exceptions import ShortURLAttributeTypeError
from shortener.domain.shorturl.fields import Slug, TargetURL, OwnerID
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


def test_change_owner_id(normal_shorturl: ShortURL):
    new_owner_id = OwnerID(UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11"))
    normal_shorturl.change_owner_id(new_owner_id)
    assert normal_shorturl.owner_id == new_owner_id


def test_change_owner_id_raises_error(normal_shorturl: ShortURL):
    with pytest.raises(ShortURLAttributeTypeError):
        normal_shorturl.change_owner_id("a") # type: ignore

