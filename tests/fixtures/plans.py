import pytest
from shortener.domain.plan import Plan


@pytest.fixture
def default_plan():
    return Plan(name="Default", max_shorturls=5)
