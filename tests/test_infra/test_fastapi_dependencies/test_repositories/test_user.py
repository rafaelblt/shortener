import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.settings import reload_settings
from shortener.infra.db.repositories import SQLAlchemyUserRepository
from shortener.infra.dependencies.fastapi.db.repositories.user import (
    get_user_repository, make_sqlalchemy_user_repository
)


def test_make_sqlalchemy_user_repository():
    from shortener.infra.db import get_session
    retrieved = make_sqlalchemy_user_repository()
    assert isinstance(retrieved, SQLAlchemyUserRepository)
    assert isinstance(retrieved.session, Depends)
    assert retrieved.session.dependency == get_session


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("sqlalchemy", make_sqlalchemy_user_repository),
        ("", make_sqlalchemy_user_repository),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["USER_REPOSITORY_IMPL"] = impl
        reload_settings()
        retrieved = get_user_repository()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
