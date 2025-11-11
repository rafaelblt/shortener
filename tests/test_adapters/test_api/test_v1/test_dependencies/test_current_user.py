import pytest

from datetime import timedelta
from http import HTTPStatus

from fastapi import HTTPException
from fastapi.params import Depends

from shortener.adapters.api.v1.dependencies.current_user import (
    CurrentUserDependency,
    get_current_user_from_request_state,
    require_authenticated_user
)
from shortener.domain.user import User

from tests.utils.type_helpers import get_annotated_args


class DummyState:
    user: User

class DummyRequest:
    def __init__(self, user):
        self.state = DummyState()
        self.state.user = user


def test_current_user_dependency():
    args = get_annotated_args(CurrentUserDependency)
    assert args[0] == User
    assert isinstance(args[1], Depends)
    assert args[1].dependency == get_current_user_from_request_state


@pytest.mark.asyncio
async def test_get_current_user_from_request_state_returns_user_instance(
    normal_user: User
):
    req = DummyRequest(normal_user)
    retrieved = await get_current_user_from_request_state(request=req) # type: ignore
    assert retrieved is normal_user


@pytest.mark.asyncio
async def test_get_current_user_from_request_state_raises_value_error():
    req = DummyRequest(None)
    with pytest.raises(
        ValueError,
        match=("No user found in the request state. Perhaps the request is missing "
               "the require_authenticated_user dependency?")
    ):
        await get_current_user_from_request_state(request=req) # type: ignore


@pytest.mark.asyncio
async def test_require_authenticated_user(
    normal_user: User,
    mock_auth_token_service,
    mock_user_repository,
    sqlalchemy_uow
):
    req = DummyRequest(None)
    user_saved = await mock_user_repository.add(normal_user)
    token = await mock_auth_token_service.generate_token(user_saved)
    retrieved = await require_authenticated_user(
        request=req, # type: ignore
        token=token.value,
        access_token_service=mock_auth_token_service,
        uow=sqlalchemy_uow
    )
    assert (retrieved.pk, retrieved.email) == (user_saved.pk, user_saved.email)
    assert (req.state.user.pk, req.state.user.email) == (user_saved.pk, user_saved.email)


@pytest.mark.asyncio
async def test_require_authenticated_user_raises_exception_with_token_invalid(
    mock_auth_token_service,
    sqlalchemy_uow
):
    req = DummyRequest(None)
    with pytest.raises(HTTPException) as exc:
        await require_authenticated_user(
            request=req, # type: ignore
            token="dsaiofju9sahfh!I*#Tihoadf#@13245",
            access_token_service=mock_auth_token_service,
            uow=sqlalchemy_uow
        )
    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Access token invalid."
    

@pytest.mark.asyncio
async def test_require_authenticated_user_raises_exception_with_token_expired(
    normal_user: User,
    mock_auth_token_service,
    mock_user_repository,
    sqlalchemy_uow
):
    req = DummyRequest(None)
    user_saved = await mock_user_repository.add(normal_user)
    mock_auth_token_service._expires_in = timedelta()
    token = await mock_auth_token_service.generate_token(user_saved)
    with pytest.raises(HTTPException) as exc:
        await require_authenticated_user(
            request=req, # type: ignore
            token=token.value,
            access_token_service=mock_auth_token_service,
            uow=sqlalchemy_uow
        )
    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Access token invalid."
