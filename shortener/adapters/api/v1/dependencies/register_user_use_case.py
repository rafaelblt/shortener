from fastapi import Depends

from shortener.domain.services.password_validator import PasswordValidatorService
from shortener.infra.services.password_hasher import PasslibPasswordHasher
from shortener.infra.services.user_validators import EmailExistsValidator

from shortener.use_cases import RegisterUserUseCase

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository
from .sqlalchemy_plan_repository import make_sqlalchemy_plan_repository


def make_register_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    plan_repository = Depends(make_sqlalchemy_plan_repository)
):
    return RegisterUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        password_hasher=PasslibPasswordHasher(),
        validators={
            "email": [EmailExistsValidator(repository=user_repository)],
            "password": [PasswordValidatorService()],
            "name": []
        }
    )
