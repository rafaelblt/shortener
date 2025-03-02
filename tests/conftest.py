from pytest import fixture

from .mocks import MockShortURLRepository

from shortener.domain.shorturl import ShortURL, SlugGenerator
from shortener.domain.shorturl.validators import (
    AvailabilityValidator as ShortURLAvailabilityValidator,
    GeneralValidator as ShortURLGeneralValidator
)

from shortener.infra.db.models import Base
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DATABASE_URL = "sqlite:///:memory:"
test_database_engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(bind=test_database_engine)


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
    Base.metadata.create_all(test_database_engine)
    with TestSession() as db:
        db.begin()
        yield db
        db.rollback()
    Base.metadata.drop_all(test_database_engine)
    

@fixture
def sqlalchemy_shorturl_repository(db_session):
    return SQLAlchemyShortURLRepository(db_session)
