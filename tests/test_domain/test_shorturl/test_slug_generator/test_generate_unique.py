from pytest import raises

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.repository import ShortURLRepository


class ExistOnlyTrueRepo(ShortURLRepository):
    def save(self, short_url: ShortURL) -> None:
        return None

    
    def exists_by_slug(self, slug: str) -> bool:
        return True

    
    def get_by_slug(self, slug: str) -> ShortURL:
        return None


def test_raises_type_error_when_repository_is_missing(shorturl_slug_generator):
    with raises(TypeError):
        shorturl_slug_generator.generate_unique_slug()


def test_return_type(shorturl_slug_generator, mock_repository):
    slug = shorturl_slug_generator.generate_unique_slug(repository=mock_repository)
    assert isinstance(slug, str)


def test_default_length(shorturl_slug_generator, mock_repository):
    slug = shorturl_slug_generator.generate_unique_slug(repository=mock_repository)
    assert len(slug) == 6


def test_custom_length(shorturl_slug_generator, mock_repository):
    slug = shorturl_slug_generator.generate_unique_slug(
        repository=mock_repository, length=10
    )
    assert len(slug) == 10


def test_raises_runtime_error_when_max_attempts_reached(shorturl_slug_generator):
    repository = ExistOnlyTrueRepo()
    max_attempts = 100

    with raises(RuntimeError) as exception:
        shorturl_slug_generator.generate_unique_slug(repository=repository)
    
    assert str(exception.value) == ("Could not generate a unique slug after "
                                    f"{max_attempts} attempts.")


def test_raises_runtime_error_with_custom_max_attempts(shorturl_slug_generator):
    repository = ExistOnlyTrueRepo()
    max_attempts = 1

    with raises(RuntimeError) as exception:
        shorturl_slug_generator.generate_unique_slug(
            repository=repository, max_attempts=max_attempts
        )
    
    assert str(exception.value) == ("Could not generate a unique slug after "
                                    f"{max_attempts} attempts.")
