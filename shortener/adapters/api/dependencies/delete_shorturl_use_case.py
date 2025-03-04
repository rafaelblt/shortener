from .sqlalchemy_shorturl_repository import make_sqlalchemy_shorturl_repository

from shortener.use_cases import DeleteShortURLUseCase


def make_delete_shorturl_use_case() -> DeleteShortURLUseCase:
    repository = make_sqlalchemy_shorturl_repository()
    return DeleteShortURLUseCase(repository)
