import pytest
from shortener.domain.plan import PlanRepository
from tests.fixtures.mocks.chameleon_repository import ChameleonMockRepository


@pytest.fixture
def mock_plan_repository():
    return ChameleonMockRepository(PlanRepository)
