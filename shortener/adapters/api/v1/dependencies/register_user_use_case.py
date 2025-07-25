from datetime import timedelta
from typing import Annotated

from fastapi import Depends

from shortener.infra.settings import settings
from shortener.infra.services.jwt_token import JwtTokenService
from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.templates.jinja import JinjaEnvironment
from shortener.infra.templates.jinja.auth import VerificationEmailTemplate

from shortener.use_cases import RegisterUserUseCase

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository
from .sqlalchemy_plan_repository import make_sqlalchemy_plan_repository
from .sendgrid_email_service import make_sendgrid_email_service


def make_register_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    plan_repository = Depends(make_sqlalchemy_plan_repository),
    send_grid_email_service = Depends(make_sendgrid_email_service)
):
    expiration_minutes = settings.EMAIL_VERIFICATION_EXPIRATION_MINUTES
    timedelta_expiration = timedelta(minutes=int(expiration_minutes))
    return RegisterUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        token_service=JwtTokenService(),
        email_verification_expires_in=timedelta_expiration,
        send_email_service=send_grid_email_service,
        password_hasher=PasslibPasswordHasher(),
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
