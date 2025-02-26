DEFAULT_RANDOM_SLUG_LENGTH = 6

SLUG_MAX_LENGTH = 30
SLUG_MIN_LENGTH = 3


def is_slug_longer_than_max_length(slug: str):
    """Checks if the slug exceeds the maximum allowed length."""
    return len(slug) > SLUG_MAX_LENGTH


def is_slug_shorter_than_min_length(slug: str):
    """Checks if the slug is shorter than the minimum allowed length."""
    return len(slug) < SLUG_MIN_LENGTH
