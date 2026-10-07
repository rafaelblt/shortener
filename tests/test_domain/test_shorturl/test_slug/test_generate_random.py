from shortener.domain.shorturl.fields.slug import (
    Slug,
    RANDOM_SLUG_LENGTH,
    RANDOM_SLUG_CHARS,
    SLUG_MAX_LENGTH,
    SLUG_MIN_LENGTH,
    SLUG_PATTERN
)


def test_returns_a_slug():
    assert isinstance(Slug.generate_random(), Slug)


def test_has_the_random_slug_length():
    assert len(Slug.generate_random()) == RANDOM_SLUG_LENGTH


def test_only_uses_the_random_slug_chars():
    assert all(char in RANDOM_SLUG_CHARS for char in Slug.generate_random())


def test_random_slug_length_is_within_the_slug_length_limits():
    assert SLUG_MIN_LENGTH <= RANDOM_SLUG_LENGTH <= SLUG_MAX_LENGTH


def test_random_slug_chars_all_match_the_slug_pattern():
    assert SLUG_PATTERN.fullmatch(RANDOM_SLUG_CHARS)
