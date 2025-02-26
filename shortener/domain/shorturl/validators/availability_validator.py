from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)

from .base_validator import ShortURLValidator


class AvailabilityValidator(ShortURLValidator):
    def __init__(self):
        pass

    def validate(self, shorturl: ShortURL) -> None:
        """
        Args:
            shorturl (ShortURL): The shorturl object to be validated.

        Returns:
            None: The shorturl object is valid.

        Raises:
            ShortURLInactiveError: If is_active attr of ShortURL is False.
            ShortURLExpiredError: If the ShortURL has expired.
        """
        if not shorturl.is_active:
            raise ShortURLInactiveError("The ShortURL is not active")
        
        expiration = shorturl.expires_at
        
        if expiration and datetime.now(tz=timezone.utc) > expiration:
            raise ShortURLExpiredError("The ShortURL has expired.")
