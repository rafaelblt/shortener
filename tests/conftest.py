from pytest import fixture

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .mocks import MockShortURLRepository

from shortener.domain.shorturl import ShortURL, SlugGenerator
from shortener.domain.shorturl.validators import (
    AvailabilityValidator as ShortURLAvailabilityValidator,
    GeneralValidator as ShortURLGeneralValidator
)

from shortener.infra.db import get_session
from shortener.infra.db.models import Base
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository

from shortener.adapters.api import app


@fixture
def normal_shorturl():
    return ShortURL(
        slug="lorem-ipsum-website",
        original_url="lorem.makeyoursite.com"
    )


@fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@fixture
def shorturl_slug_generator():
    return SlugGenerator()


@fixture
def shorturl_availability_validator():
    return ShortURLAvailabilityValidator()


@fixture
def shorturl_general_validator(mock_shorturl_repository):
    return ShortURLGeneralValidator(repository=mock_shorturl_repository)


@fixture
def db_session():
    TEST_DATABASE_URL = "sqlite:///:memory:"
    test_database_engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestSession = sessionmaker(bind=test_database_engine)

    Base.metadata.create_all(test_database_engine)
    with TestSession() as db:
        db.begin()
        yield db
        db.rollback()
    Base.metadata.drop_all(test_database_engine)
    

@fixture
def sqlalchemy_shorturl_repository(db_session):
    return SQLAlchemyShortURLRepository(db_session)


@fixture
def client(db_session):

    def session_override():
        return db_session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = session_override
        yield client

    app.dependency_overrides.clear()
