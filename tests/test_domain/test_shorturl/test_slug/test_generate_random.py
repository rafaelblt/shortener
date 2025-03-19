from shortener.domain.shorturl.slug import (
    Slug,
    DEFAULT_RANDOM_SLUG_LENGTH,
    DEFAULT_CHARS,
    SLUG_PATTERN
)


def test_instance():
    random_slug = Slug.generate_random()
    assert isinstance(random_slug, Slug)


def test_default_random_slug_length():
    random_slug = Slug.generate_random()
    assert len(random_slug) == DEFAULT_RANDOM_SLUG_LENGTH


def test_slug_pattern():
    random_slug = Slug.generate_random()
    assert SLUG_PATTERN.match(random_slug)


def test_default_chars():
    random_slug = Slug.generate_random()
    assert all(char in DEFAULT_CHARS for char in random_slug)


def test_generate_with_custom_length():
    custom_length = 15
    random_slug = Slug.generate_random(length=custom_length)
    assert isinstance(random_slug, Slug)
    assert len(random_slug) == custom_length


def test_generate_with_custom_chars():
    custom_chars = "abc123"
    random_slug = Slug.generate_random(chars=custom_chars)
    assert isinstance(random_slug, Slug)
    assert all(char in custom_chars for char in random_slug)
    assert SLUG_PATTERN.match(random_slug)


def test_generate_with_custom_length_and_chars():
    custom_length = 9
    custom_chars = "xyz789"
    random_slug = Slug.generate_random(length=custom_length, chars=custom_chars)
    assert isinstance(random_slug, Slug)
    assert len(random_slug) == custom_length
    assert all(char in custom_chars for char in random_slug)
    assert SLUG_PATTERN.match(random_slug)
