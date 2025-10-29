from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from shortener.domain.services.exceptions import TokenExpiredError, TokenInvalidError
from shortener.domain.user import User

from .services import AccessTokenServiceDependency
from .uow import UnitOfWorkDependency


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user_from_request_state(request: Request) -> User:
    user = request.state.user
    if not isinstance(user, User):
        raise ValueError(
            ("No user found in the request state. Perhaps the request is missing "
             "the require_authenticated_user dependency?")
        )
    return request.state.user


async def require_authenticated_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    access_token_service: AccessTokenServiceDependency,
    uow: UnitOfWorkDependency
) -> User:
    try:
        async with uow.transaction():
            user = await access_token_service.decode_token(token)
    except (TokenInvalidError, TokenExpiredError):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Access token invalid."
        )
    request.state.user = user
    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user_from_request_state)]
