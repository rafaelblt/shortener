from typing import Annotated

from fastapi import Depends

from shortener.infra.settings import settings
from shortener.infra.services.jwt_token import JwtTokenService
from shortener.infra.templates.jinja import JinjaEnvironment
from shortener.infra.templates.jinja.auth import VerificationEmailTemplate

from shortener.use_cases import RegisterUserUseCase

from . import (
    make_sqlalchemy_user_repository,
    make_sqlalchemy_plan_repository,
    make_sendgrid_email_service,
    make_passlib_password_hasher
)


def make_register_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    plan_repository = Depends(make_sqlalchemy_plan_repository),
    send_grid_email_service = Depends(make_sendgrid_email_service),
    password_hasher = Depends(make_passlib_password_hasher)
):
    expiration = settings.EMAIL_VERIFICATION_EXPIRATION
    return RegisterUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        token_service=JwtTokenService(),
        email_verification_expires_in=expiration,
        send_email_service=send_grid_email_service,
        password_hasher=password_hasher,
        email_template=VerificationEmailTemplate(JinjaEnvironment()),
        validators_map={
            "email": [],
            "password": [],
            "name": []
        }
    )


RegisterUserUseCaseDependency = Annotated[
    RegisterUserUseCase, Depends(make_register_user_use_case)
]
