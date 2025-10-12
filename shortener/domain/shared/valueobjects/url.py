from urllib.parse import ParseResult, urlparse

from shortener.domain.shared.exceptions import ValidationError


class InvalidURLError(ValidationError):
    code = "INVALID_URL"
    def __init__(self, url: str):
        self.url = url
        msg = "Invalid URL."
        super().__init__(value=url, field="url", code=self.code, message=msg)


class URL(str):
    """A custom string class representing a URL"""
    _parsed: ParseResult

    def __new__(cls, value: str):
        obj = super().__new__(cls, value)
        obj._parsed = cls._parse_url(value)
        if not obj._parsed.scheme or not obj._parsed.netloc:
            raise InvalidURLError(value)
        return obj

    def __repr__(self):
        return f"<URL({super().__repr__()})>"

    @classmethod
    def validate(cls, value: str) -> None:
        parsed = cls._parse_url(value)
        if not parsed.scheme or not parsed.netloc:
            raise InvalidURLError(value)
    
    @staticmethod
    def _parse_url(value: str):
        try:
            return urlparse(value)
        except (ValueError, TypeError):
            raise InvalidURLError(value)

    def is_https(self) -> bool:
        return self._parsed.scheme == "https"
