from shortener.infra.dependencies.fastapi.db.repositories import get_shorturl_repository
from shortener.use_cases import ListShortURLUseCase


def make_list_shorturl_use_case(
    repository = get_shorturl_repository()
):
    return ListShortURLUseCase(repository=repository)
