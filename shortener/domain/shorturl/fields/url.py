from urllib.parse import urlparse

from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


class URL(str):
    """A custom string class representing a URL for ShortURL"""

    def __new__(cls, value: str):
        cls.validate_url(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<URL({super().__repr__()})>"

    @classmethod
    def validate_url(cls, value: str):
        if not cls.is_valid_https_url(value):
            raise ShortURLInvalidURLError("URL must be a valid https url.")

    @staticmethod
    def is_valid_https_url(url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            return parsed_url.scheme == "https" and bool(parsed_url.netloc)
        except:
            return False
