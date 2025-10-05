from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository
from shortener.infra.dependencies.fastapi.use_cases import make_list_shorturl_use_case

from shortener.use_cases import ListShortURLUseCase


def test_dependency_factory():
    retrieved = make_list_shorturl_use_case()
    assert isinstance(retrieved, ListShortURLUseCase)
    assert isinstance(retrieved.repository, Depends)
    assert retrieved.repository.dependency == get_shorturl_repository().dependency
