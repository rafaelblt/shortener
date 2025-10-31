from typing import Annotated

from shortener.infra.dependencies import fastapi_deps

from shortener.domain.services.token import AuthTokenService


AccessTokenServiceDependency = Annotated[
    AuthTokenService, fastapi_deps.access_token_service
]
