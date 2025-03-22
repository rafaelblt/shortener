import re
import string
import random

from typing import Final
from shortener.domain.shorturl.repository import ShortURLRepository
from shortener.domain.shorturl.exceptions import (
    ShortURLSlugTooLongError,
    ShortURLSlugTooShortError,
    ShortURLForbiddenSlugError,
    ShortURLInvalidSlugError
)


DEFAULT_RANDOM_SLUG_LENGTH: Final = 6
SLUG_MAX_LENGTH: Final = 30
SLUG_MIN_LENGTH: Final = 3

DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG = 100

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
        cls._validate_slug(value)
        return super().__new__(cls, value)

    def __repr__(self):
        return f"<Slug({super().__repr__()})>"
    
    @staticmethod
    def _validate_slug(value: str):
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
            raise ShortURLInvalidSlugError(
                "Slug contains invalid characters. Allowed: a-z, A-Z, 0-9, _, -"
            )

        if value.lower() in FORBIDDEN_SLUGS:
            raise ShortURLForbiddenSlugError(
                "The provided slug is forbidden."
            )

        if len(value) < SLUG_MIN_LENGTH:
            raise ShortURLSlugTooShortError(
                f"Slug must be at least {SLUG_MIN_LENGTH} characters long."
            )
        
        if len(value) > SLUG_MAX_LENGTH:
            raise ShortURLSlugTooLongError(
                f"Slug must be at most {SLUG_MAX_LENGTH} characters long."
            )

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


async def generate_unique_slug( 
    repository: ShortURLRepository, 
    length: int = DEFAULT_RANDOM_SLUG_LENGTH,
    max_attempts: int = DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG
) -> Slug:
    """
    Generates a unique slug of a specified length.

    This method generates a random slug and checks its uniqueness against 
    the provided repository. If the slug already exists, it continues 
    generating new slugs until a unique one is found or until max_attempts 
    is reached.

    Args:
        repository (ShortURLRepository): The repository to check for 
            existing slugs.
        length (Optional[int]): The length of the slug to generate. 
        max_attempts (Optional[int]): The maximum number of attempts 
            to generate a unique slug.

    Returns:
        Slug: A unique slug.

    Raises:
        RuntimeError: If a unique slug cannot be found within max_attempts.
    """
    attempts = 0

    while attempts <= max_attempts:
        attempts += 1
        slug = Slug.generate_random(length=length)
        
        if not await repository.exists_by_slug(slug):
            return slug

    raise RuntimeError(
        f"Could not generate a unique slug after {max_attempts} attempts."
    )
