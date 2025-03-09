import pytest
import pytest_asyncio

from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

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


@pytest.fixture
def normal_shorturl():
    return ShortURL(
        slug="lorem-ipsum-website",
        original_url="lorem.makeyoursite.com"
    )


@pytest.fixture
def other_shorturl():
    return ShortURL(
        slug="other-network",
        original_url="www.git.com"
    )


@pytest.fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@pytest.fixture
def shorturl_slug_generator():
    return SlugGenerator()


@pytest.fixture
def shorturl_availability_validator():
    return ShortURLAvailabilityValidator()


@pytest.fixture
def shorturl_general_validator(mock_shorturl_repository):
    return ShortURLGeneralValidator(repository=mock_shorturl_repository)


@pytest_asyncio.fixture
async def db_session():
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    test_database_engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestSession = sessionmaker(bind=test_database_engine, class_=AsyncSession)

    async with test_database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        yield session
    
    async with test_database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_database_engine.dispose()


@pytest_asyncio.fixture
async def sqlalchemy_shorturl_repository(db_session):
    return SQLAlchemyShortURLRepository(db_session)


@pytest.fixture
def client(db_session):

    def session_override():
        return db_session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = session_override
        yield client

    app.dependency_overrides.clear()
