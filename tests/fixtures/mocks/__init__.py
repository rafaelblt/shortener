import pytest

from .shorturl_repository import MockShortURLRepository
from .user_repository import MockUserRepository
from .plan_repository import MockPlanRepository


@pytest.fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()


@pytest.fixture
def mock_plan_repository():
    return MockPlanRepository()
