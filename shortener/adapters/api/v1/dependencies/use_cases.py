from typing import Annotated

from shortener.infra.dependencies import fastapi_deps

from shortener.use_cases import (
    CreateShortURLForUserUseCase,
    CreateShortURLUseCase,
    DeleteShortURLUseCase,
    GetShortURLUseCase,
    ListShortURLUseCase,
    ReadShortURLOfUserUseCase,
    ResolveShortURLUseCase,
    UpdateShortURLUseCase,
    VerifyEmailUseCase,
    LoginUserUseCase,
    RefreshLoginUseCase,
    RegisterUserUseCase,
)


CreateShortURLForUserUseCaseDependency = Annotated[
    CreateShortURLForUserUseCase, fastapi_deps.create_shorturl_for_user_use_case
]
CreateShortURLUseCaseDependency = Annotated[
    CreateShortURLUseCase, fastapi_deps.create_shorturl_use_case
]
DeleteShortURLUseCaseDependency = Annotated[
    DeleteShortURLUseCase, fastapi_deps.delete_shorturl_use_case
]
GetShortURLUseCaseDependency = Annotated[
    GetShortURLUseCase, fastapi_deps.get_shorturl_use_case
]
ListShortURLUseCaseDependency = Annotated[
    ListShortURLUseCase, fastapi_deps.list_shorturl_use_case
]
ResolveShortURLUseCaseDependency = Annotated[
    ResolveShortURLUseCase, fastapi_deps.resolve_shorturl_use_case
]
ReadShortURLOfUserUseCaseDependency = Annotated[
    ReadShortURLOfUserUseCase, fastapi_deps.read_shorturl_of_user_use_case
]
UpdateShortURLUseCaseDependency = Annotated[
    UpdateShortURLUseCase, fastapi_deps.update_shorturl_use_case
]

VerifyEmailUseCaseDependency = Annotated[
    VerifyEmailUseCase, fastapi_deps.verify_email_use_case
]
LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, fastapi_deps.login_user_use_case
]
RefreshLoginUseCaseDependency = Annotated[
    RefreshLoginUseCase, fastapi_deps.refresh_login_use_case
]
RegisterUserUseCaseDependency = Annotated[
    RegisterUserUseCase, fastapi_deps.register_user_use_case
]
