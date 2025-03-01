from pytest import fixture, raises

from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)

from shortener.use_cases import ResolveShortURLUseCase


@fixture
def repository(mock_shorturl_repository, normal_shorturl):
    mock_shorturl_repository.save(normal_shorturl)
    return mock_shorturl_repository


@fixture
def use_case(repository, shorturl_availability_validator):
    return ResolveShortURLUseCase(
        repository=repository,
        validator=shorturl_availability_validator
    )


def test_resolve_slug_with_nonexistent_slug(use_case):
    original_url = use_case.resolve_slug("nonexistent-slug")
    assert original_url is None


def test_resolve_slug_with_normal_shorturl(use_case, normal_shorturl):
    original_url = use_case.resolve_slug(normal_shorturl.slug)
    assert original_url == normal_shorturl.original_url


def test_resolve_slug_raises_shorturl_inactive(use_case, normal_shorturl):
    normal_shorturl.is_active = False

    with raises(ShortURLInactiveError, match="The ShortURL is not active"):
        use_case.resolve_slug(normal_shorturl.slug)


def test_resolve_slug_raises_shorturl_expired(use_case, normal_shorturl):
    normal_shorturl.expires_at = normal_shorturl.created_at

    with raises(ShortURLExpiredError, match="The ShortURL has expired"):
        use_case.resolve_slug(normal_shorturl.slug)
