from typing import Annotated
from fastapi import Depends

from shortener.infra.services.jwt_token import JwtTokenService

from shortener.use_cases import VerifyEmailUseCase

from . import make_sqlalchemy_user_repository


def make_verify_email_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
):
    return VerifyEmailUseCase(
        user_repository=user_repository,
        token_service=JwtTokenService()
    )

VerifyEmailUseCaseDependency = Annotated[
    VerifyEmailUseCase, Depends(make_verify_email_use_case)
]
