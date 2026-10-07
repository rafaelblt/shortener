import re
import string

from shortener.domain.shorturl.slug import (
    RANDOM_SLUG_LENGTH,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH,
    RANDOM_SLUG_CHARS,
    SLUG_PATTERN
)


def test_random_slug_length():
    assert RANDOM_SLUG_LENGTH == 6


def test_slug_max_length():
    assert SLUG_MAX_LENGTH == 30


def test_slug_min_length():
    assert SLUG_MIN_LENGTH == 3


def test_random_slug_chars():
    assert RANDOM_SLUG_CHARS == string.ascii_letters + string.digits


def test_slug_pattern():
    assert isinstance(SLUG_PATTERN, re.Pattern)
    assert SLUG_PATTERN.pattern == r"^[a-zA-Z0-9_-]+$"
