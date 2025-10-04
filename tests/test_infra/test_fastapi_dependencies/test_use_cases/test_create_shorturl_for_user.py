from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.infra.dependencies.fastapi.use_cases import make_create_shorturl_for_user_use_case

from shortener.use_cases import CreateShortURLForUserUseCase


def test_dependency_factory():
    retrieved = make_create_shorturl_for_user_use_case()
    assert isinstance(retrieved, CreateShortURLForUserUseCase)
    assert isinstance(retrieved.shorturl_repository, Depends)
    assert retrieved.shorturl_repository.dependency == get_shorturl_repository().dependency
