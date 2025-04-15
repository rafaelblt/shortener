from shortener.domain.shorturl import ShortURL


def test_is_expired_true(expired_shorturl: ShortURL):
    assert expired_shorturl.is_expired


def test_is_expired_false(normal_shorturl: ShortURL):
    assert normal_shorturl.is_expired is False


def test_is_available_true(normal_shorturl: ShortURL):
    assert normal_shorturl.is_available


def test_is_available_false(expired_shorturl: ShortURL):
    assert expired_shorturl.is_available is False

