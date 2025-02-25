import random
import string

from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.shorturl.rules.slug_length import (
    DEFAULT_RANDOM_SLUG_LENGTH as RANDOM_LENGTH
)


class SlugGenerator:
    """A class used to generate slugs for URLs"""
    
    def __init__(self):
        self.chars = string.ascii_letters + string.digits

    def generate_random_slug(self, length: int = RANDOM_LENGTH) -> str:
        """
        Generate a random slug of a specified length.
        Args:
            length (int): The length of the slug to generate.
        Returns:
            str: A randomly generated slug.
        """
        return "".join(random.choices(self.chars, k=length))
    
    def generate_unique_slug(
            self, 
            repository: ShortURLRepository, 
            length: int = RANDOM_LENGTH,
            max_attempts: int = 100
        ) -> str:
        """
        Generates a unique slug of a specified length.
        This method generates a random slug and checks its uniqueness against 
        the provided repository. If the slug already exists, it continues 
        generating new slugs until a unique one is found or until max_attempts 
        is reached.

        Args:
            repository (ShortURLRepository): The repository to check for 
                existing slugs.
            length (int, optional): The length of the slug to generate. 
            max_attempts (int, optional): The maximum number of attempts 
                to generate a unique slug. Default is 100.

        Returns:
            str: A unique slug.

        Raises:
            RuntimeError: If a unique slug cannot be found within max_attempts.
        """
        attempts = 0

        while attempts <= max_attempts:
            attempts += 1
            slug = self.generate_random_slug(length=length)
            if not repository.exists_by_slug(slug):
                return slug

        raise RuntimeError(
            f"Could not generate a unique slug after {max_attempts} attempts."
        )
