from pytest import fixture, raises

from shortener.domain.shorturl.exceptions import ShortURLDeletionNotFoundError

from shortener.use_cases import DeleteShortURLUseCase


@fixture
def use_case(mock_shorturl_repository, normal_shorturl):
    normal_shorturl.id = 1
    mock_shorturl_repository.save(normal_shorturl)
    return DeleteShortURLUseCase(repository=mock_shorturl_repository)


def test_delete_by_id(use_case, normal_shorturl):
    retrieved = use_case.delete_by_id(normal_shorturl.id)
    assert retrieved.id == normal_shorturl.id
    assert retrieved.slug == normal_shorturl.slug


def test_raises_not_found_delete_by_id(use_case):
    example_id = 2
    with raises(
        ShortURLDeletionNotFoundError,
        match=f"ShortURL with id {example_id} not found for deletion."
    ):
        use_case.delete_by_id(example_id)
