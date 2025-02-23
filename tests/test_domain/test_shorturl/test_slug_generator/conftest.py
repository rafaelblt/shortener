from pytest import fixture

from shortener.domain.shorturl.slug_generator import SlugGenerator


@fixture
def generator():
    return SlugGenerator()
