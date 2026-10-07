import re
import string
import random

from typing import Final

from shortener.domain.shared.parsing import require_non_empty_string
from shortener.domain.shared.result import Result
from shortener.domain.shared.validation import StringValidation, ValidationError


DEFAULT_RANDOM_SLUG_LENGTH: Final = 6
SLUG_MAX_LENGTH: Final = 30
SLUG_MIN_LENGTH: Final = 3

DEFAULT_CHARS: Final = string.ascii_letters + string.digits
SLUG_PATTERN: Final = re.compile(r"^[a-zA-Z0-9_-]+$")


class Slug(str):
    """A custom string class representing a Slug for ShortURL"""

    def __new__(cls, value: str) -> "Slug":
        """
        Prefer create(), which returns the broken rules instead of raising.

        Raises:
            ValueError: The value breaks a rule of create(). Its only argument
                is the ValidationError.
        """
        return cls.create(value).unwrap()

    def __repr__(self):
        return f"<Slug({super().__repr__()})>"

    @classmethod
    def create(cls, value: object) -> Result["Slug", ValidationError]:
        return (
            StringValidation(value)
            .matches(SLUG_PATTERN)
            .min_length(SLUG_MIN_LENGTH)
            .max_length(SLUG_MAX_LENGTH)
            .result()
            .map(cls._build)
        )

    @classmethod
    def parse(cls, value: object) -> "Slug":
        """
        Only checks that the value is a non-empty str, so a slug created under
        older rules is still accepted. See docs/domain.md#value-objects

        Raises:
            TypeError: The value isn't a str.
            ValueError: The value is empty.
        """
        return cls._build(require_non_empty_string(value, cls.__name__))

    @classmethod
    def generate_random(
        cls,
        length: int = DEFAULT_RANDOM_SLUG_LENGTH,
        chars: str = DEFAULT_CHARS
    ) -> Result["Slug", ValidationError]:
        random_slug = "".join(random.choices(chars, k=length))
        return cls.create(random_slug)

    @classmethod
    def _build(cls, value: str) -> "Slug":
        return super().__new__(cls, value)
