import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.settings import reload_settings
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository
from shortener.infra.dependencies.fastapi.db.repositories.shorturl import (
    get_shorturl_repository, make_sqlalchemy_shorturl_repository
)


def test_make_sqlalchemy_shorturl_repository():
    from shortener.infra.db import get_session
    retrieved = make_sqlalchemy_shorturl_repository()
    assert isinstance(retrieved, SQLAlchemyShortURLRepository)
    assert isinstance(retrieved.session, Depends)
    assert retrieved.session.dependency == get_session


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("sqlalchemy", make_sqlalchemy_shorturl_repository),
        ("", make_sqlalchemy_shorturl_repository),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["SHORTURL_REPOSITORY_IMPL"] = impl
        reload_settings()
        retrieved = get_shorturl_repository()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
