import copy

from pytest import fixture, raises

from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)
from shortener.use_cases import ResolveShortURLUseCase


@fixture
def use_case(
    mock_shorturl_repository, shorturl_availability_validator, normal_shorturl
):
    repository = copy.deepcopy(mock_shorturl_repository)
    repository.save(normal_shorturl)
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
    use_case.repository.data[1]["is_active"] = False

    with raises(ShortURLInactiveError, match="The ShortURL is not active"):
        use_case.resolve_slug(normal_shorturl.slug)


def test_resolve_slug_raises_shorturl_expired(use_case, normal_shorturl):
    expire_datetime = use_case.repository.data[1]["created_at"]
    use_case.repository.data[1]["expires_at"] = expire_datetime

    with raises(ShortURLExpiredError, match="The ShortURL has expired"):
        use_case.resolve_slug(normal_shorturl.slug)
