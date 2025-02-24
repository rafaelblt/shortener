from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL

from .base_validator import ShortURLValidator


class AvailabilitShortURLyValidator(ShortURLValidator):
    def __init__(self):
        pass

    def validate(self, shorturl: ShortURL):
        """
        
        """
        if not shorturl.is_active:
            raise Exception()
        
        expiration = shorturl.expires_at
        now = datetime.now(tz=timezone.utc)
        
        if expiration and now > expiration:
            raise Exception("The short URL has expired.")
