from typing import Annotated
from fastapi import Depends

from shortener.use_cases import CreateShortURLUseCase

from . import make_sqlalchemy_shorturl_repository


def make_create_shorturl_use_case(
    shorturl_repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return CreateShortURLUseCase(shorturl_repository=shorturl_repository)


CreateShortURLUseCaseDependency = Annotated[
    CreateShortURLUseCase, Depends(make_create_shorturl_use_case)
]
