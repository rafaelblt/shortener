import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.db.session import get_session
from shortener.infra.dependencies.fastapi.services.refresh_token import (
    make_sqlalchemy_refresh_auth_token_service,
    get_refresh_auth_token_service,
)
from shortener.infra.services.refresh_token import SQLAlchemyRefreshAuthTokenService
from shortener.infra.settings import get_settings, reload_settings


def test_make_sqlalchemy_refresh_auth_token_service():
    settings = get_settings()
    retrieved = make_sqlalchemy_refresh_auth_token_service()
    assert isinstance(retrieved, SQLAlchemyRefreshAuthTokenService)
    assert isinstance(retrieved.session, Depends)
    assert retrieved.session.dependency == get_session
    assert retrieved.expires_in == settings.refresh_token_expiration


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("sqlalchemy", make_sqlalchemy_refresh_auth_token_service),
        ("", make_sqlalchemy_refresh_auth_token_service),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["REFRESH_TOKEN_SERVICE_IMPL"] = impl
        reload_settings()
        retrieved = get_refresh_auth_token_service()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
