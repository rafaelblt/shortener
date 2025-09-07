from typing import Annotated
from fastapi import Depends

from shortener.use_cases import CreateShortURLForUserUseCase

from . import make_sqlalchemy_shorturl_repository


def make_create_shorturl_for_user_use_case(
    shorturl_repository = Depends(make_sqlalchemy_shorturl_repository)
):
    return CreateShortURLForUserUseCase(shorturl_repository=shorturl_repository)


CreateShortURLForUserUseCaseDependency = Annotated[
    CreateShortURLForUserUseCase, Depends(make_create_shorturl_for_user_use_case)
]
