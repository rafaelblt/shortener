from datetime import timedelta
import pytest

from fastapi.params import Depends

from shortener.infra.services.urlsafe_token import URLSafeTokenGenerator
from shortener.infra.settings import settings

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_token import JwtTokenService

from shortener.use_cases import LoginUserUseCase

from shortener.adapters.api.v1.dependencies import (
    make_login_user_use_case,
    make_sqlalchemy_user_repository,
    make_sqlalchemy_refresh_token_repository,
    LoginUserUseCaseDependency
)

from tests.utils.type_helpers import get_annotated_args


@pytest.fixture
def use_case():
    return make_login_user_use_case()


def test_instance(use_case: LoginUserUseCase):
    assert isinstance(use_case, LoginUserUseCase)


def test_attr_user_repository(use_case: LoginUserUseCase):
    assert isinstance(use_case.user_repository, Depends)
    assert use_case.user_repository.dependency == make_sqlalchemy_user_repository


def test_attr_refresh_token_repository(use_case: LoginUserUseCase):
    assert isinstance(use_case.refresh_token_repository, Depends)
    assert use_case.refresh_token_repository.dependency == make_sqlalchemy_refresh_token_repository


def test_attr_password_hasher(use_case: LoginUserUseCase):
    assert isinstance(use_case.password_hasher, PasslibPasswordHasher)


def test_attr_access_token_service(use_case: LoginUserUseCase):
    assert isinstance(use_case.access_token_service, JwtTokenService)
    assert use_case.access_token_service._secret_key == settings.JWT_SECRET_KEY
    assert use_case.access_token_service._algorithm == settings.JWT_ALGORITHM


def test_attr_access_token_expires_in(use_case: LoginUserUseCase):
    assert isinstance(use_case.access_token_expires_in, timedelta)
    assert use_case.access_token_expires_in == settings.ACCESS_TOKEN_EXPIRATION


def test_attr_refresh_token_generator(use_case: LoginUserUseCase):
    assert isinstance(use_case.refresh_token_generator, URLSafeTokenGenerator)


def test_attr_refresh_token_expires_in(use_case: LoginUserUseCase):
    assert isinstance(use_case.refresh_token_expires_in, timedelta)
    assert use_case.refresh_token_expires_in == settings.REFRESH_TOKEN_EXPIRATION


def test_dependency():
    args = get_annotated_args(LoginUserUseCaseDependency)
    assert args[0] == LoginUserUseCase
    assert isinstance(args[1], Depends)
    assert args[1].dependency == make_login_user_use_case
