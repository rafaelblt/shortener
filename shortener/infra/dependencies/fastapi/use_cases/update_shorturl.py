from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository
from shortener.use_cases import UpdateShortURLUseCase


def make_update_shorturl_use_case(
    shorturl_repository = get_shorturl_repository()
):
    return UpdateShortURLUseCase(
        shorturl_repository=shorturl_repository
    )
