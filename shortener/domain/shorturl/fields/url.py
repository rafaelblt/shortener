from shortener.domain.shared.valueobjects.url import URL, InvalidURLError
from shortener.domain.shorturl.exceptions import ShortURLInvalidURLError


class OriginalURL(URL):
    """A custom string class representing the original_url of ShortURL"""

    def __new__(cls, value: str):
        try:
            original_url = super().__new__(cls, value)
        except InvalidURLError as e:
            raise ShortURLInvalidURLError(e.url)
        if not original_url.is_https():
            raise ShortURLInvalidURLError(original_url)
        return original_url

    def __repr__(self):
        return f"<OriginalURL({super().__str__()})>"

    @classmethod
    def validate(cls, value: str):
        try:
            url = URL(value)
        except InvalidURLError as e:
            raise ShortURLInvalidURLError(e.url)
        if not url.is_https():
            raise ShortURLInvalidURLError(url)
