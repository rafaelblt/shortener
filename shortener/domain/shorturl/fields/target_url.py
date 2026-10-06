from urllib.parse import urlparse

from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


class TargetURL(str):

    def __new__(cls, value: str):
        cls.validate_target_url(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<TargetURL({super().__repr__()})>"

    @staticmethod
    def validate_target_url(value: str) -> None:
        """
        Raises:
            ShortURLInvalidURLError: The value isn't an https URL with a host.
        """
        try:
            parsed = urlparse(value)
        except (ValueError, TypeError):
            raise ShortURLInvalidURLError(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ShortURLInvalidURLError(value)
