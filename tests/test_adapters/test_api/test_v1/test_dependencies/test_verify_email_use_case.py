import pytest

from fastapi.params import Depends

from shortener.infra.services.jwt_auth_token import JwtAuthTokenService
from shortener.infra.settings import settings

from shortener.adapters.api.v1.dependencies import make_verify_email_use_case

from shortener.use_cases import VerifyEmailUseCase

from shortener.adapters.api.v1.dependencies import (
    make_verify_email_use_case,
    make_sqlalchemy_user_repository
)


@pytest.fixture
def use_case():
    return make_verify_email_use_case()


def test_instance(use_case: VerifyEmailUseCase):
    assert isinstance(use_case, VerifyEmailUseCase)


def test_attr_user_repository(use_case: VerifyEmailUseCase):
    assert isinstance(use_case.user_repository, Depends)
    assert use_case.user_repository.dependency == make_sqlalchemy_user_repository


def test_attr_auth_token_service(use_case: VerifyEmailUseCase):
    assert isinstance(use_case.auth_token_service, JwtAuthTokenService)
    assert use_case.auth_token_service._secret_key == settings.JWT_AUTH_SECRET_KEY
    assert use_case.auth_token_service._algorithm == settings.JWT_AUTH_TOKEN_ALGORITHM
    assert use_case.auth_token_service.expires_minutes == settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES
