import pytest
from shortener.domain.user import UserRepository
from tests.fixtures.mocks.chameleon_repository import ChameleonMockRepository


@pytest.fixture
def mock_user_repository():
    return ChameleonMockRepository(UserRepository)
