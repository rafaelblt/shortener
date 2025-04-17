import re
import string

from shortener.domain.shorturl.fields.slug import (
    DEFAULT_RANDOM_SLUG_LENGTH,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH,
    DEFAULT_CHARS,
    SLUG_PATTERN,
    FORBIDDEN_SLUGS
)


def test_default_random_slug_length():
    assert DEFAULT_RANDOM_SLUG_LENGTH == 6


def test_slug_max_length():
    assert SLUG_MAX_LENGTH == 30


def test_slug_min_length():
    assert SLUG_MIN_LENGTH == 3


def test_default_chars():
    assert DEFAULT_CHARS == string.ascii_letters + string.digits


def test_slug_pattern():
    assert isinstance(SLUG_PATTERN, re.Pattern)
    assert SLUG_PATTERN.pattern == r"^[a-zA-Z0-9_-]+$"


def test_forbidden_slugs():
    expected_forbidden_slugs = {
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
    assert FORBIDDEN_SLUGS == expected_forbidden_slugs
