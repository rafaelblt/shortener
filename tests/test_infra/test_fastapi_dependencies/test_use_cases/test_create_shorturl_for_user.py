from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository, get_user_repository
from shortener.infra.dependencies.fastapi.use_cases import make_create_shorturl_for_user_use_case

from shortener.use_cases import CreateShortURLForUserUseCase


def test_dependency_factory():
    retrieved = make_create_shorturl_for_user_use_case()
    assert isinstance(retrieved, CreateShortURLForUserUseCase)
    assert isinstance(retrieved.shorturl_repo, Depends)
    assert retrieved.shorturl_repo.dependency == get_shorturl_repository().dependency
    assert isinstance(retrieved.user_repo, Depends)
    assert retrieved.user_repo.dependency == get_user_repository().dependency
