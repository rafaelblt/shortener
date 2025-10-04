from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.infra.dependencies.fastapi.use_cases import make_update_shorturl_use_case

from shortener.use_cases import UpdateShortURLUseCase


def test_dependency_factory():
    retrieved = make_update_shorturl_use_case()
    assert isinstance(retrieved, UpdateShortURLUseCase)
    assert isinstance(retrieved.shorturl_repository, Depends)
    assert retrieved.shorturl_repository.dependency == get_shorturl_repository().dependency
