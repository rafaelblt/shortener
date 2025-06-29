from typing import Annotated
from fastapi import Depends

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService

from shortener.use_cases import LoginUserUseCase

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository


def make_login_user_use_case(
    repository = Depends(make_sqlalchemy_user_repository)
):
    return LoginUserUseCase(
        user_repository=repository,
        password_hasher=PasslibPasswordHasher(),
        auth_token_service=JwtAuthTokenService()
    )


LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, Depends(make_login_user_use_case)
]
