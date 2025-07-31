from fastapi import Depends

from . import make_sqlalchemy_shorturl_repository

from shortener.use_cases import ListShortURLUseCase


def make_list_shorturl_use_case(
    repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return ListShortURLUseCase(repository=repository)
