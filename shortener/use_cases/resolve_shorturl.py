from shortener.domain.shorturl import ShortURLRepository, ShortURLValidator


class ResolveShortURLUseCase:
    """Use case to resolve a ShortURL object"""

    def __init__(
            self, repository: ShortURLRepository, validator: ShortURLValidator
        ):
        """
        Args:
            repository (ShortURLRepository):
            validator (ShortURLValidator): 
        """
        self.repository = repository
        self.validator = validator
    
    def resolve_slug(self, slug: str) -> str:
        """
        Args:
            slug (str):

        Returns:
            str: The original_url of ShortURL
        """
        shorturl = self.repository.get_by_slug(slug)

        self.validator.validate(shorturl)

        return shorturl.original_url
