from shortener.infra.dependencies.fastapi.repositories import get_shorturl_repository
from shortener.use_cases import DeleteShortURLUseCase


def make_delete_shorturl_use_case(
    repository = get_shorturl_repository()
):
    return DeleteShortURLUseCase(repository)
