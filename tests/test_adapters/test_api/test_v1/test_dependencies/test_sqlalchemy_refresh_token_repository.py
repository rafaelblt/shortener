import pytest

from fastapi.params import Depends

from shortener.adapters.api.v1.dependencies import (
    make_sqlalchemy_refresh_token_repository
)

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyRefreshTokenRepository


@pytest.fixture
def repository():
    return make_sqlalchemy_refresh_token_repository()


def test_instance(repository: SQLAlchemyRefreshTokenRepository):
    assert isinstance(repository, SQLAlchemyRefreshTokenRepository)


def test_attr_session(repository: SQLAlchemyRefreshTokenRepository):
    assert isinstance(repository.session, Depends)
    assert repository.session.dependency == get_session
