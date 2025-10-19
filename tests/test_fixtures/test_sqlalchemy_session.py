from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


def test_sqlalchemy_engine(sqlalchemy_engine):
    assert isinstance(sqlalchemy_engine, AsyncEngine)


def test_sqlalchemy_session_factory(sqlalchemy_session_factory):
    assert isinstance(sqlalchemy_session_factory, sessionmaker)


def test_sqlalchemy_session(sqlalchemy_session):
    assert isinstance(sqlalchemy_session, AsyncSession)
