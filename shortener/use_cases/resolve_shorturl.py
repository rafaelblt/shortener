from shortener.domain.shorturl import ShortURLRepository, ShortURLValidator


class ResolveShortURLUseCase:
    """Use case to resolve a ShortURL object"""

    def __init__(
            self, 
            repository: ShortURLRepository, 
            validator: ShortURLValidator
        ):
        """
        Args:
            repository (ShortURLRepository): The repository to get the ShortURL.
            validator (ShortURLValidator): The validator to validate the object.
        """
        self.repository = repository
        self.validator = validator
    
    def resolve_slug(self, slug: str) -> str:
        """
        Get the original_url attr of a ShortURL in the repository with the slug.

        Args:
            slug (str): The ShortURL slug to be resolved.

        Returns:
            str: The original_url of ShortURL
        """
        shorturl = self.repository.get_by_slug(slug)

        self.validator.validate(shorturl)

        return shorturl.original_url
