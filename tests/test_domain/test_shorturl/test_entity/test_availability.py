from shortener.domain.shorturl import ShortURL


def test_is_available_when_active(normal_shorturl: ShortURL):
    assert normal_shorturl.is_available() is True


def test_is_not_available_when_deactivated(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    assert normal_shorturl.is_available() is False
