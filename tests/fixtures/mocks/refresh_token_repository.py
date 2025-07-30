import pytest
from shortener.domain.refresh_token import RefreshTokenRepository
from tests.fixtures.mocks.chameleon_repository import ChameleonMockRepository


@pytest.fixture
def mock_refresh_token_repository():
    return ChameleonMockRepository(RefreshTokenRepository)
