import pytest

from fastapi.params import Depends

from shortener.domain.services.password_validator import PasswordStrengthValidator
from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService
from shortener.infra.services.sendgrid_email import SendGridEmailService
from shortener.infra.services.user_validators import EmailExistsValidator

from shortener.use_cases import RegisterUserUseCase

from shortener.adapters.api.v1.dependencies import (
    make_register_user_use_case,
    make_sqlalchemy_user_repository,
    make_sqlalchemy_plan_repository
)


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


def test_attr_auth_token_service(use_case: RegisterUserUseCase):
    assert isinstance(use_case.auth_token_service, JwtAuthTokenService)


def test_attr_send_email_service(use_case: RegisterUserUseCase):
    assert isinstance(use_case.send_email_service, Depends)
    assert use_case.send_email_service.dependency == SendGridEmailService


def test_attr_password_hasher(use_case: RegisterUserUseCase):
    assert isinstance(use_case.password_hasher, PasslibPasswordHasher)


def test_attr_validators(use_case: RegisterUserUseCase):
    assert isinstance(use_case.validators, dict)

    assert "email" in use_case.validators
    assert "password" in use_case.validators
    assert "name" in use_case.validators

    email_validators = use_case.validators["email"]
    password_validators = use_case.validators["password"]
    name_validators = use_case.validators["name"]

    assert isinstance(email_validators, list)
    assert isinstance(password_validators, list)
    assert isinstance(name_validators, list)

    assert len(email_validators) == 1
    assert len(password_validators) == 1
    assert len(name_validators) == 0

    assert isinstance(email_validators[0], EmailExistsValidator)
    assert isinstance(password_validators[0], PasswordStrengthValidator)

    assert isinstance(email_validators[0].repository, Depends)
    assert email_validators[0].repository.dependency == make_sqlalchemy_user_repository
