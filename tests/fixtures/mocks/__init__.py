import pytest

from .shorturl_repository import MockShortURLRepository
from .user_repository import MockUserRepository


@pytest.fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()
