from typing import Annotated

from shortener.infra.dependencies import fastapi_deps

from shortener.domain.user import UserRepository


UserRepositoryDependency = Annotated[
    UserRepository, fastapi_deps.user_repository
]
