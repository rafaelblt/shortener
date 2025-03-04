from typing import Optional
from datetime import datetime

from shortener.domain.shorturl import (
    ShortURL, 
    ShortURLRepository,
    ShortURLValidator,
    SlugGenerator,
)


class CreateShortURLUseCase:
    """Use case to create a new ShortURL object and save in repository."""

    def __init__(
            self, 
            repository: ShortURLRepository, 
            validator: ShortURLValidator,
            slug_generator: SlugGenerator,
        ):
        """
        Initializes the use case with a repository, validatior and slug generator.

        Args:
            repository (ShortURLRepository): Repository to save the ShortURL object.
            validator (ShortURLValidator): Validator to validate the ShortURL data.
            slug_generator (SlugGenerator): Generator to generate unique slugs.
        """
        self.repository = repository
        self.validator = validator
        self.slug_generator = slug_generator

    def execute(
            self, 
            original_url: str, 
            owner_id: Optional[int] = None, 
            custom_slug: Optional[str] = None, 
            expires_at: Optional[datetime] = None
        ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (str): The original_url to be shortened.
            owner_id (Optional[int]): User ID who created the ShortURL.
            custom_slug (Optional[str]): Custom slug of the ShortURL.
            expires_at (Optional[datetime]): Expiration date of the ShortURL.

        Returns:
            ShortURL: The ShortURL object.
        """
        slug = custom_slug or self.slug_generator.generate_unique_slug(
            repository=self.repository
        )

        shorturl = ShortURL(
            slug=slug,
            original_url=original_url,
            owner_id=owner_id,
            expires_at=expires_at
        )

        self.validator.validate(shorturl)
        
        self.repository.save(shorturl)

        return shorturl
