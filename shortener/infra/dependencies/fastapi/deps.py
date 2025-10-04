from typing import Callable
from dataclasses import dataclass, field

from fastapi import Depends
from fastapi.params import Depends as DependsClass

from shortener.domain.plan import PlanRepository
from shortener.domain.services.password_hasher import PasswordHasherService
from shortener.domain.services.send_email import SendEmailService
from shortener.domain.services.token import AuthTokenService
from shortener.domain.shorturl import ShortURLRepository
from shortener.domain.user import UserRepository

from shortener.use_cases import (
    CreateShortURLForUserUseCase,
    CreateShortURLUseCase,
    DeleteShortURLUseCase,
    GetShortURLUseCase,
    ListShortURLUseCase,
    LoginUserUseCase,
    RefreshLoginUseCase,
    RegisterUserUseCase,
    ResolveShortURLUseCase,
    UpdateShortURLUseCase,
    VerifyEmailUseCase
)

from .repositories import (
    get_plan_repository, get_shorturl_repository, get_user_repository
)
from .services import (
    get_access_auth_token_service,
    get_verify_email_auth_token_service,
    get_password_hasher_service,
    get_refresh_auth_token_service,
    get_send_email_service
)
from .use_cases import (
    make_create_shorturl_for_user_use_case,
    make_create_shorturl_use_case,
    make_delete_shorturl_use_case,
    make_get_shorturl_use_case,
    make_list_shorturl_use_case,
    make_login_user_use_case,
    make_refresh_login_use_case,
    make_register_user_use_case,
    make_resolve_shorturl_use_case,
    make_update_shorturl_use_case,
    make_verify_email_use_case,
)


def wrap_with_depends(func: Callable):
    def factory():
        return Depends(func)
    return factory


@dataclass(frozen=True)
class FastApiDependencies:
    plan_repository: DependsClass = field(default_factory=get_plan_repository)
    shorturl_repository: DependsClass = field(default_factory=get_shorturl_repository)
    user_repository: DependsClass = field(default_factory=get_user_repository)

    access_token_service: DependsClass = field(default_factory=get_access_auth_token_service)
    verify_email_token_service: DependsClass = field(default_factory=get_verify_email_auth_token_service)
    password_hasher_service: DependsClass = field(default_factory=get_password_hasher_service)
    refresh_token_service: DependsClass = field(default_factory=get_refresh_auth_token_service)
    send_email_service: DependsClass = field(default_factory=get_send_email_service)

    register_user_use_case: DependsClass = field(default_factory=wrap_with_depends(make_register_user_use_case))
    login_user_use_case: DependsClass = field(default_factory=wrap_with_depends(make_login_user_use_case))
    verify_email_use_case: DependsClass = field(default_factory=wrap_with_depends(make_verify_email_use_case))
    refresh_login_use_case: DependsClass = field(default_factory=wrap_with_depends(make_refresh_login_use_case))
    create_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_create_shorturl_use_case))
    create_shorturl_for_user_use_case: DependsClass = field(default_factory=wrap_with_depends(make_create_shorturl_for_user_use_case))
    delete_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_delete_shorturl_use_case))
    get_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_get_shorturl_use_case))
    list_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_list_shorturl_use_case))
    resolve_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_resolve_shorturl_use_case))
    update_shorturl_use_case: DependsClass = field(default_factory=wrap_with_depends(make_update_shorturl_use_case))

    @classmethod
    def load(cls) -> "FastApiDependencies":
        return FastApiDependencies()
    

fastapi_deps = FastApiDependencies.load()
