from shortener.infra.dependencies.fastapi.services import get_verify_email_auth_token_service
from shortener.infra.dependencies.fastapi.db.repositories import get_user_repository

from shortener.use_cases import VerifyEmailUseCase


def make_verify_email_use_case(
    token_service = get_verify_email_auth_token_service(),
    user_repository = get_user_repository(),
):
    return VerifyEmailUseCase(
        user_repository=user_repository,
        token_service=token_service
    )
