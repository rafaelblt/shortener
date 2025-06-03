import pytest
import pytest_asyncio

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundError, PlanIdIsNotIntError

from shortener.infra.db.repositories import SQLAlchemyPlanRepository


@pytest_asyncio.fixture
async def repository(sqlalchemy_plan_repository):
    return sqlalchemy_plan_repository


@pytest.mark.asyncio
async def test_add(repository: SQLAlchemyPlanRepository, default_plan: Plan):
    retrieved = await repository.add(default_plan)
    assert isinstance(retrieved, Plan)
    assert retrieved.id == 1
    assert retrieved.name == default_plan.name


@pytest.mark.asyncio
async def test_update(repository: SQLAlchemyPlanRepository, default_plan: Plan):
    plan = await repository.add(default_plan)
    plan._name = "Test New Name"
    plan._max_shorturls = 100

    retrieved = await repository.update(plan)

    assert isinstance(retrieved, Plan)
    assert retrieved.name == plan.name
    assert retrieved.max_shorturls == plan.max_shorturls


@pytest.mark.asyncio
async def test_update_plan_without_id_raises_error(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    with pytest.raises(PlanIdIsNotIntError) as error:
        await repository.update(default_plan)
    assert error.value.value == None


@pytest.mark.asyncio
async def test_update_plan_with_id_non_existent_raises_error(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    default_plan._id = 1
    with pytest.raises(PlanNotFoundError) as error:
        await repository.update(default_plan)
    assert error.value.plan_id == default_plan.id


@pytest.mark.asyncio
async def test_get_all_with_no_plans(repository: SQLAlchemyPlanRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_plans(
    repository: SQLAlchemyPlanRepository, 
    default_plan: Plan,
):
    other_plan = Plan(name="other test plan", max_shorturls=10)

    await repository.add(default_plan)
    await repository.add(other_plan)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 2
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], Plan)
        assert retrieved[i].id == expected_id
    assert retrieved[0].name == default_plan.name
    assert retrieved[1].name == other_plan.name


@pytest.mark.asyncio
async def test_get_by_id(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    await repository.add(default_plan)

    retrieved = await repository.get_by_id(1)

    assert isinstance(retrieved, Plan)
    assert retrieved.id == 1
    assert retrieved.name == default_plan.name


@pytest.mark.asyncio
async def test_delete_by_id(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    await repository.add(default_plan)

    retrieved = await repository.delete_by_id(1)

    assert isinstance(retrieved, Plan)
    assert retrieved.id == 1
    assert retrieved.name == default_plan.name
    assert await repository.get_by_id(1) is None


@pytest.mark.asyncio
async def test_delete_by_id_non_existent_plan(
    repository: SQLAlchemyPlanRepository
):
    with pytest.raises(PlanNotFoundError) as error:
        await repository.delete_by_id(1)
    assert error.value.plan_id == 1
