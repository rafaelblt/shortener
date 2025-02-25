from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import InactiveShortURL, ShortURLExpired

from .base_validator import ShortURLValidator


class AvailabilityValidator(ShortURLValidator):
    def __init__(self):
        pass

    def validate(self, shorturl: ShortURL) -> None:
        """
        Raises:
            InactiveShortURL:
            ShortURLExpired:
        """
        if not shorturl.is_active:
            raise InactiveShortURL("The ShortURL is not active")
        
        expiration = shorturl.expires_at
        
        if expiration and datetime.now(tz=timezone.utc) > expiration:
            raise ShortURLExpired("The ShortURL has expired.")
