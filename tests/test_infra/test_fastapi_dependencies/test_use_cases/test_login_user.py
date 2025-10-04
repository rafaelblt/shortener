from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.repositories import get_user_repository
from shortener.infra.dependencies.fastapi.services import (
    get_password_hasher_service,
    get_access_auth_token_service,
    get_refresh_auth_token_service
)
from shortener.infra.dependencies.fastapi.use_cases import make_login_user_use_case

from shortener.use_cases import LoginUserUseCase


def test_dependency_factory():
    retrieved = make_login_user_use_case()

    assert isinstance(retrieved, LoginUserUseCase)

    assert isinstance(retrieved.user_repository, Depends)
    assert retrieved.user_repository.dependency == get_user_repository().dependency

    assert isinstance(retrieved.password_hasher, Depends)
    assert retrieved.password_hasher.dependency == get_password_hasher_service().dependency

    assert isinstance(retrieved.access_token_service, Depends)
    assert retrieved.access_token_service.dependency == get_access_auth_token_service().dependency
    
    assert isinstance(retrieved.refresh_token_service, Depends)
    assert retrieved.refresh_token_service.dependency == get_refresh_auth_token_service().dependency
