import pytest
from shortener.domain.plan import Plan


@pytest.fixture
def default_plan():
    return Plan(name="Default", max_shorturls=5)


@pytest.fixture
def eco_plan():
    return Plan(name="Eco", max_shorturls=10)
