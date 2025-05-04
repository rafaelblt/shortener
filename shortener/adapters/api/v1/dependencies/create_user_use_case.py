from fastapi import Depends

from shortener.use_cases import CreateUserUseCase

from shortener.infra.services.password_hasher import PasslibPasswordHasher
from shortener.infra.validators.user_validators import UserCreateValidator

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository
from .sqlalchemy_plan_repository import make_sqlalchemy_plan_repository


def make_create_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    plan_repository = Depends(make_sqlalchemy_plan_repository)
):
    return CreateUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        password_hasher=PasslibPasswordHasher(),
        validator=UserCreateValidator(repository=user_repository)
    )
