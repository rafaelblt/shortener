from pytest import fixture

from shortener.use_cases import GetShortURLUseCase


@fixture
def use_case(mock_shorturl_repository, normal_shorturl):
    normal_shorturl.id = 1
    mock_shorturl_repository.save(normal_shorturl)
    return GetShortURLUseCase(repository=mock_shorturl_repository)


def test_get_by_id(use_case, normal_shorturl):
    retrieved = use_case.get_by_id(1)
    assert retrieved.slug == normal_shorturl.slug


def test_get_by_id_non_existent(use_case):
    retrieved = use_case.get_by_id(2)
    assert retrieved is None


def test_get_by_slug(use_case, normal_shorturl):
    retrieved = use_case.get_by_slug(normal_shorturl.slug)
    assert retrieved.original_url == normal_shorturl.original_url


def test_get_by_slug_non_existent(use_case):
    retrieved = use_case.get_by_slug("non-existent-slug")
    assert retrieved is None
