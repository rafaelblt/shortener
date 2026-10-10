from shortener.domain import ShortURLID


def test_generate_returns_a_shorturl_id_with_a_uuid7():
    shorturl_id = ShortURLID.generate()
    assert isinstance(shorturl_id, ShortURLID)
    assert shorturl_id.value.version == 7


def test_generate_returns_a_new_id_each_time():
    assert ShortURLID.generate() != ShortURLID.generate()
