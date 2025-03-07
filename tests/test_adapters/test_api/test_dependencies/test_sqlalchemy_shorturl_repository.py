import pytest

from fastapi.params import Depends

from shortener.adapters.api.dependencies import make_sqlalchemy_shorturl_repository

from shortener.infra.db import get_session
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@pytest.fixture
def repository():
    return make_sqlalchemy_shorturl_repository()


def test_instance(repository: SQLAlchemyShortURLRepository):
    assert isinstance(repository, SQLAlchemyShortURLRepository)


def test_attr_session(repository: SQLAlchemyShortURLRepository):
    assert isinstance(repository.session, Depends)
    assert repository.session.dependency == get_session
