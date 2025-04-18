from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import ShortURLStatus


def test_if_status_is_updated(expired_shorturl: ShortURL):
    assert expired_shorturl.status == ShortURLStatus.EXPIRED
