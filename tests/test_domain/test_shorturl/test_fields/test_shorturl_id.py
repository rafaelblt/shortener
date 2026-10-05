from shortener.domain.shorturl.fields import ShortURLID


def test_generate_returns_a_shorturl_id():
    assert isinstance(ShortURLID.generate(), ShortURLID)


def test_generate_uses_uuid_version_7():
    assert ShortURLID.generate().value.version == 7


def test_generate_returns_a_new_id_each_time():
    assert ShortURLID.generate() != ShortURLID.generate()
