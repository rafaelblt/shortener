from fastapi import Depends

from .sqlalchemy_shorturl_repository import make_sqlalchemy_shorturl_repository

from shortener.use_cases import DeleteShortURLUseCase


def make_delete_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository) 
):
    return DeleteShortURLUseCase(repository)
