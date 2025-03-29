from urllib.parse import urlparse


class URL(str):
    """A custom string class representing a URL for ShortURL"""

    def __new__(cls, value: str):
        cls.validate_url(value)
        return super().__new__(cls, value)

    @classmethod
    def validate_url(cls, value: str):
        """
        Validate the URL value.

        Args:
            value (str): The URL to be validated.
        
        Returns: 
            None: The URL is valid.

        Raises:
            ...
        """
        if not cls.is_valid_https_url(value):
            pass

    @staticmethod
    def is_valid_https_url(url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.scheme == "https"
