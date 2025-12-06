from shortener.infra.dependencies.fastapi.db.repositories import get_user_repository
from shortener.use_cases.read_shorturl_of_user import ReadShortURLOfUserUseCase


def make_read_shorturl_of_user_use_case(
    user_repository = get_user_repository()
):
    return ReadShortURLOfUserUseCase(
        user_repository=user_repository
    )
