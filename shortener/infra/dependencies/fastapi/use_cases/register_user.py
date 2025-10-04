from shortener.infra.dependencies.fastapi.services import (
    get_verify_email_auth_token_service,
    get_send_email_service,
    get_password_hasher_service
)
from shortener.infra.dependencies.fastapi.repositories import (
    get_user_repository,
    get_plan_repository
)
from shortener.infra.templates.jinja import JinjaEnvironment
from shortener.infra.templates.jinja.auth import VerificationEmailTemplate

from shortener.use_cases import RegisterUserUseCase




def make_register_user_use_case(
    token_service = get_verify_email_auth_token_service(),
    user_repository = get_user_repository(),
    plan_repository = get_plan_repository(),
    send_grid_email_service = get_send_email_service(),
    password_hasher = get_password_hasher_service(),
):
    return RegisterUserUseCase(
        user_repository=user_repository,
        plan_repository=plan_repository,
        token_service=token_service,
        send_email_service=send_grid_email_service,
        password_hasher=password_hasher,
        email_template=VerificationEmailTemplate(JinjaEnvironment()),
    )
