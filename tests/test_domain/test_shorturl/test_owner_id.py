from uuid import UUID

from shortener.domain.shorturl import OwnerID, ShortURLID


VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")


def test_keeps_the_value():
    assert OwnerID(VALUE).value == VALUE


def test_is_not_equal_to_a_shorturl_id_with_the_same_value():
    assert OwnerID(VALUE) != ShortURLID(VALUE)
