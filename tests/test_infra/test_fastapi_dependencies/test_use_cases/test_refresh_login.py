from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.services import (
    get_access_auth_token_service,
    get_refresh_auth_token_service
)
from shortener.infra.dependencies.fastapi.use_cases import make_refresh_login_use_case

from shortener.use_cases import RefreshLoginUseCase


def test_dependency_factory():
    retrieved = make_refresh_login_use_case()

    assert isinstance(retrieved, RefreshLoginUseCase)

    assert isinstance(retrieved.access_token_service, Depends)
    assert retrieved.access_token_service.dependency == get_access_auth_token_service().dependency
    
    assert isinstance(retrieved.refresh_token_service, Depends)
    assert retrieved.refresh_token_service.dependency == get_refresh_auth_token_service().dependency
