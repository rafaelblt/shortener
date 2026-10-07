import re
import string
import random

from typing import Final
from shortener.domain.shorturl.exceptions import (
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError,
    ShortURLForbiddenSlugError,
    ShortURLInvalidSlugError
)


DEFAULT_RANDOM_SLUG_LENGTH: Final = 6
SLUG_MAX_LENGTH: Final = 30
SLUG_MIN_LENGTH: Final = 3

DEFAULT_CHARS: Final = string.ascii_letters + string.digits
SLUG_PATTERN: Final = re.compile(r"^[a-zA-Z0-9_-]+$")

FORBIDDEN_SLUGS = {
    "docs",
    "admin", 
    "login", 
    "logout", 
    "dashboard", 
    "api", 
    "config", 
    "help", 
    "support", 
    "terms", 
    "privacy", 
    "about", 
    "contact"
}


class Slug(str):
    """A custom string class representing a Slug for ShortURL"""

    def __new__(cls, value: str):
        value = str(value)
        cls.validate_slug(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<Slug({super().__repr__()})>"
    
    @staticmethod
    def validate_slug(value: str):
        """
        Validate the Slug value.

        Args:
            value (str): The slug to be validated.
        
        Returns: 
            None: The slug is valid.

        Raises:
            ShortURLInvalidSlugError: The slug contains invalid characters.
            ShortURLForbiddenSlugError: The slug is forbidden.
            ShortURLSlugTooLongError: The slug is longer than max length.
            ShortURLSlugTooShortError: The slug is shorther than min length.
        """
        if not SLUG_PATTERN.match(value):
            raise ShortURLInvalidSlugError(slug=value)

        if value.lower() in FORBIDDEN_SLUGS:
            raise ShortURLForbiddenSlugError(value)

        if len(value) < SLUG_MIN_LENGTH:
            raise ShortURLSlugTooShortError(slug=value, min_length=SLUG_MIN_LENGTH)
        
        if len(value) > SLUG_MAX_LENGTH:
            raise ShortURLSlugTooLongError(slug=value, max_length=SLUG_MAX_LENGTH)

    @classmethod
    def generate_random(
        cls, 
        length: int = DEFAULT_RANDOM_SLUG_LENGTH,
        chars: str = DEFAULT_CHARS
    ) -> "Slug":
        """
        Generate a random slug with a specified length and chars.

        Args:
            length (int): The length of the slug to generate.
            chars (str): The chars to use for generate.
        
        Returns:
            str: A randomly generated slug.
        """
        random_slug = "".join(random.choices(chars, k=length))
        return cls(random_slug)
