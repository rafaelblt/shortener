from typing import Annotated

from fastapi import Depends

from shortener.domain.user.validators import EmailAlreadyExistsValidator
from shortener.domain.services.password_validator import PasswordStrengthValidator

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.services.jwt_auth_token import JwtAuthTokenService
from shortener.infra.services.sendgrid_email import SendGridEmailService
from shortener.infra.templates.jinja import JinjaEnvironment
from shortener.infra.templates.jinja.auth import VerificationEmailTemplate

from shortener.use_cases import RegisterUserUseCase

from .sqlalchemy_user_repository import make_sqlalchemy_user_repository
from .sqlalchemy_plan_repository import make_sqlalchemy_plan_repository


def make_register_user_use_case(
    user_repository = Depends(make_sqlalchemy_user_repository),
    plan_repository = Depends(make_sqlalchemy_plan_repository),
    send_grid_email_service = Depends(SendGridEmailService)
):        
    return RegisterUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        auth_token_service=JwtAuthTokenService(),
        send_email_service=send_grid_email_service,
        password_hasher=PasslibPasswordHasher(),
        email_template=VerificationEmailTemplate(JinjaEnvironment()),
        validators={
            "email": [EmailAlreadyExistsValidator(repository=user_repository)],
            "password": [PasswordStrengthValidator()],
            "name": []
        }
    )


RegisterUserUseCaseDependency = Annotated[
    RegisterUserUseCase, Depends(make_register_user_use_case)
]
