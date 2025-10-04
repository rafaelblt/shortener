from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.infra.dependencies.fastapi.use_cases import make_resolve_shorturl_use_case

from shortener.use_cases import ResolveShortURLUseCase


def test_dependency_factory():
    retrieved = make_resolve_shorturl_use_case()
    assert isinstance(retrieved, ResolveShortURLUseCase)
    assert isinstance(retrieved.repository, Depends)
    assert retrieved.repository.dependency == get_shorturl_repository().dependency
