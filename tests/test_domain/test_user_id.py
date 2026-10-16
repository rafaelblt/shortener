from uuid import UUID

from shortener.domain import ShortURLID, UserID


def test_is_not_equal_to_a_shorturl_id_with_the_same_value():
    value = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
    assert UserID(value) != ShortURLID(value)
