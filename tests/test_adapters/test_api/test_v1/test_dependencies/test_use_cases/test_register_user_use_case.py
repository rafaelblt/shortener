import pytest

from datetime import timedelta

from fastapi.params import Depends

from shortener.infra.settings import settings
from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_token import JwtTokenService
from shortener.infra.services.sendgrid_email import SendGridEmailService
from shortener.infra.services.user_validators import EmailExistsValidator

from shortener.use_cases import RegisterUserUseCase

from shortener.adapters.api.v1.dependencies import (
    make_register_user_use_case,
    make_sqlalchemy_user_repository,
    make_sqlalchemy_plan_repository,
    RegisterUserUseCaseDependency
)

from tests.utils.type_helpers import get_annotated_args


@pytest.fixture
def use_case():
    return make_register_user_use_case()


def test_instance(use_case: RegisterUserUseCase):
    assert isinstance(use_case, RegisterUserUseCase)


def test_attr_user_repository(use_case: RegisterUserUseCase):
    assert isinstance(use_case.user_repository, Depends)
    assert use_case.user_repository.dependency == make_sqlalchemy_user_repository


def test_attr_plan_repository(use_case: RegisterUserUseCase):
    assert isinstance(use_case.plan_repository, Depends)
    assert use_case.plan_repository.dependency == make_sqlalchemy_plan_repository


def test_attr_token_service(use_case: RegisterUserUseCase):
    assert isinstance(use_case.token_service, JwtTokenService)


def test_attr_send_email_service(use_case: RegisterUserUseCase):
    assert isinstance(use_case.send_email_service, Depends)
    assert use_case.send_email_service.dependency == SendGridEmailService


def test_attr_password_hasher(use_case: RegisterUserUseCase):
    assert isinstance(use_case.password_hasher, PasslibPasswordHasher)


def test_attr_email_verification_expires_in(use_case: RegisterUserUseCase):
    assert isinstance(use_case.email_verification_expires_in, timedelta)
    assert (
        use_case.email_verification_expires_in == 
        settings.EMAIL_VERIFICATION_EXPIRATION
    )


def test_attr_validators(use_case: RegisterUserUseCase):
    assert isinstance(use_case.validators_map, dict)

    assert "email" in use_case.validators_map
    assert "password" in use_case.validators_map
    assert "name" in use_case.validators_map

    email_validators = use_case.validators_map["email"]
    password_validators = use_case.validators_map["password"]
    name_validators = use_case.validators_map["name"]

    assert isinstance(email_validators, list)
    assert isinstance(password_validators, list)
    assert isinstance(name_validators, list)

    assert len(email_validators) == 0
    assert len(password_validators) == 0
    assert len(name_validators) == 0


def test_dependency():
    args = get_annotated_args(RegisterUserUseCaseDependency)
    assert args[0] == RegisterUserUseCase
    assert isinstance(args[1], Depends)
    assert args[1].dependency == make_register_user_use_case
