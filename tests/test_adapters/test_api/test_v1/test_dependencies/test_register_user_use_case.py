import pytest

from fastapi.params import Depends

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.infra.services.password_hasher import PasslibPasswordHasher
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
    assert (
        use_case.user_repository.dependency == make_sqlalchemy_user_repository
    )


def test_attr_plan_repository(use_case: RegisterUserUseCase):
    assert isinstance(use_case.plan_repository, Depends)
    assert (
        use_case.plan_repository.dependency == 
        make_sqlalchemy_plan_repository
    )


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
    assert isinstance(password_validators[0], PasswordValidatorService)

    assert isinstance(email_validators[0].repository, Depends)
    assert email_validators[0].repository.dependency == make_sqlalchemy_user_repository
