def test_return_type(shorturl_slug_generator):
    slug = shorturl_slug_generator.generate_random_slug()
    assert isinstance(slug, str)


def test_default_length(shorturl_slug_generator):
    slug = shorturl_slug_generator.generate_random_slug()
    assert len(slug) == 6


def test_custom_length(shorturl_slug_generator):
    slug = shorturl_slug_generator.generate_random_slug(length=10)
    assert len(slug) == 10
