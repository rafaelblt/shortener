import pytest

from datetime import timedelta
from fastapi.params import Depends

from shortener.adapters.api.v1.dependencies import (
    RefreshLoginUseCaseDependency,
    make_refresh_login_use_case,
    make_sqlalchemy_refresh_token_repository
)

from shortener.infra.settings import settings
from shortener.infra.services.urlsafe_token import URLSafeTokenGenerator
from shortener.infra.services.jwt_token import JwtTokenService

from shortener.use_cases.refresh_login import RefreshLoginUseCase

from tests.utils.type_helpers import get_annotated_args


@pytest.fixture
def use_case():
    return make_refresh_login_use_case()


def test_annotated_dependency():
    args = get_annotated_args(RefreshLoginUseCaseDependency)
    assert args[0] == RefreshLoginUseCase
    assert isinstance(args[1], Depends)
    assert args[1].dependency == make_refresh_login_use_case


def test_instance(use_case: RefreshLoginUseCase):
    assert isinstance(use_case, RefreshLoginUseCase)


def test_attr_refresh_token_repository(use_case: RefreshLoginUseCase):
    assert isinstance(use_case.refresh_token_repository, Depends)
    assert use_case.refresh_token_repository.dependency == make_sqlalchemy_refresh_token_repository


def test_attr_access_token_service(use_case: RefreshLoginUseCase):
    assert isinstance(use_case.access_token_service, JwtTokenService)
    assert use_case.access_token_service._secret_key == settings.JWT_SECRET_KEY
    assert use_case.access_token_service._algorithm == settings.JWT_ALGORITHM


def test_attr_access_token_expires_in(use_case: RefreshLoginUseCase):
    assert isinstance(use_case.access_token_expires_in, timedelta)
    assert use_case.access_token_expires_in == settings.ACCESS_TOKEN_EXPIRATION


def test_attr_refresh_token_generator(use_case: RefreshLoginUseCase):
    assert isinstance(use_case.refresh_token_generator, URLSafeTokenGenerator)


def test_attr_refresh_token_expires_in(use_case: RefreshLoginUseCase):
    assert isinstance(use_case.refresh_token_expires_in, timedelta)
    assert use_case.refresh_token_expires_in == settings.REFRESH_TOKEN_EXPIRATION
