import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.db.repositories import get_user_repository
from shortener.infra.dependencies.fastapi.services.access_token import (
    make_jwt_access_auth_token_service,
    get_access_auth_token_service,
    TOKEN_PURPOSE
)
from shortener.infra.services.jwt_token import JwtAuthTokenService
from shortener.infra.settings import get_settings, reload_settings


def test_make_jwt_access_auth_token_service():
    settings = get_settings()
    retrieved = make_jwt_access_auth_token_service()
    assert isinstance(retrieved, JwtAuthTokenService)
    assert retrieved._purpose == TOKEN_PURPOSE
    assert retrieved._expires_in == settings.access_token_expiration
    assert isinstance(retrieved._user_repo, Depends)
    assert retrieved._user_repo.dependency == get_user_repository().dependency


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("sqlalchemy", make_jwt_access_auth_token_service),
        ("", make_jwt_access_auth_token_service),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["ACCESS_TOKEN_SERVICE_IMPL"] = impl
        reload_settings()
        retrieved = get_access_auth_token_service()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
