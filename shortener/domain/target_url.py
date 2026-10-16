from collections.abc import Callable
from urllib.parse import urlparse

from shortener.shared.parsing import require_non_empty_string
from shortener.shared.result import Result
from shortener.shared.validation import (
    IssueCode,
    StringValidation,
    ValidationError,
)


class TargetURL(str):
    def __new__(cls, value: str) -> "TargetURL":
        """
        Prefer create(), which returns the broken rules instead of raising.

        Raises:
            ValueError: The value breaks a rule of create(). Its only argument
                is the ValidationError.
        """
        return cls.create(value).unwrap()

    def __repr__(self) -> str:
        return f"<TargetURL({super().__repr__()})>"

    def __reduce__(self) -> tuple[Callable[[object], "TargetURL"], tuple[str]]:
        # copy and pickle rebuild an instance with the constructor, which
        # would reject a value accepted under older rules. A copy is of a
        # value that already exists, so it uses parse(). See
        # docs/domain.md#value-objects
        return (type(self).parse, (str(self),))

    @classmethod
    def create(cls, value: object) -> Result["TargetURL", ValidationError]:
        return (
            StringValidation(value)
            .satisfies(_is_https_url_with_host, IssueCode.INVALID_FORMAT)
            .result()
            .map(cls._build)
        )

    @classmethod
    def parse(cls, value: object) -> "TargetURL":
        """
        Only checks that the value is a non-empty str, so a target URL created
        under older rules is still accepted. See docs/domain.md#value-objects

        Raises:
            TypeError: The value isn't a str.
            ValueError: The value is empty.
        """
        return cls._build(require_non_empty_string(value, cls.__name__))

    @classmethod
    def _build(cls, value: str) -> "TargetURL":
        return super().__new__(cls, value)


def _is_https_url_with_host(value: str) -> bool:
    # urlparse removes some of these characters before parsing, so they are
    # checked first.
    if not _is_printable_without_spaces(value):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme == "https" and bool(parsed.netloc)


def _is_printable_without_spaces(value: str) -> bool:
    # isprintable() is false for the characters of the Unicode categories
    # Other, such as control characters, and Separator, except the space.
    # See docs/domain.md#targeturl
    return value.isprintable() and " " not in value
