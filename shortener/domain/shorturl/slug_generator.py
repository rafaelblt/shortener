import random
import string


class SlugGenerator:

    def generate_slug(self, length: int = 6) -> str:
        """Generate a random slug"""
        return "".join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
