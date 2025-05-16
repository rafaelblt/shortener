import pytest

from fastapi.params import Depends

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.infra.services.password_hasher import PasslibPasswordHasher
from shortener.infra.validators.user_validators import UserCreateValidator

from shortener.use_cases import CreateUserUseCase

from shortener.adapters.api.v1.dependencies import (
    make_create_user_use_case,
    make_sqlalchemy_user_repository,
    make_sqlalchemy_plan_repository
)


@pytest.fixture
def use_case():
    return make_create_user_use_case()


def test_instance(use_case: CreateUserUseCase):
    assert isinstance(use_case, CreateUserUseCase)


def test_attr_user_repository(use_case: CreateUserUseCase):
    assert isinstance(use_case.user_repository, Depends)
    assert (
        use_case.user_repository.dependency == make_sqlalchemy_user_repository
    )


def test_attr_plan_repository(use_case: CreateUserUseCase):
    assert isinstance(use_case.plan_repository, Depends)
    assert (
        use_case.plan_repository.dependency == 
        make_sqlalchemy_plan_repository
    )


def test_attr_password_hasher(use_case: CreateUserUseCase):
    assert isinstance(use_case.password_hasher, PasslibPasswordHasher)


def test_attr_password_validator(use_case: CreateUserUseCase):
    assert isinstance(use_case.password_validator, PasswordValidatorService)


def test_attr_user_validator(use_case: CreateUserUseCase):
    assert isinstance(use_case.user_validator, UserCreateValidator)
    assert isinstance(use_case.user_validator.repository, Depends)
    assert (
        use_case.user_validator.repository.dependency ==
        make_sqlalchemy_user_repository
    )
