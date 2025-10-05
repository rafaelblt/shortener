from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.db.repositories import get_user_repository
from shortener.infra.dependencies.fastapi.services import get_verify_email_auth_token_service
from shortener.infra.dependencies.fastapi.use_cases import make_verify_email_use_case

from shortener.use_cases import VerifyEmailUseCase


def test_dependency_factory():
    retrieved = make_verify_email_use_case()

    assert isinstance(retrieved, VerifyEmailUseCase)

    assert isinstance(retrieved.user_repository, Depends)
    assert retrieved.user_repository.dependency == get_user_repository().dependency
    
    assert isinstance(retrieved.token_service, Depends)
    assert retrieved.token_service.dependency == get_verify_email_auth_token_service().dependency
