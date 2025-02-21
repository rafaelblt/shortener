import random
import string

from shortener.domain.shorturl import ShortURLRepository


class SlugGenerator:
    
    def __init__(self):
        self.chars = string.ascii_letters + string.digits

    def generate_random_slug(self, length: int = 6) -> str:
        """Generate a random slug"""
        return "".join(random.choices(self.chars, k=length))
    
    def generate_unique_slug(
            self, repository: ShortURLRepository, length: int = 6
        ) -> str:
        
        slug = self.generate_random_slug(length=length)

        while repository.exists_by_slug(slug):
            slug = self.generate_random_slug(length=length)

        return slug
