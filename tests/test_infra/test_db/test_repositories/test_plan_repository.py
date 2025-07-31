import pytest
import pytest_asyncio

from shortener.domain.plan import Plan
from shortener.domain.plan.exceptions import PlanNotFoundError, PlanIdIsNotIntError

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.infra.db.repositories import SQLAlchemyPlanRepository

from tests.utils.entity_helpers import assert_plan_fields


@pytest_asyncio.fixture
async def repository(sqlalchemy_plan_repository):
    return sqlalchemy_plan_repository


@pytest.mark.asyncio
async def test_add(repository: SQLAlchemyPlanRepository, default_plan: Plan):
    retrieved = await repository.add(default_plan)
    assert isinstance(retrieved, Plan)
    assert retrieved.pk.get_id() == 1
    assert retrieved.name == default_plan.name


@pytest.mark.asyncio
async def test_get_by_pk(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    saved_plan = await repository.add(default_plan)

    retrieved = await repository.get_by_pk(saved_plan.pk)

    assert isinstance(retrieved, Plan)
    assert_plan_fields(retrieved, saved_plan)


@pytest.mark.asyncio
async def test_update(repository: SQLAlchemyPlanRepository, default_plan: Plan):
    saved_plan = await repository.add(default_plan)

    saved_plan._name = "Test New Name"
    saved_plan._max_shorturls = 100

    retrieved = await repository.update(saved_plan)
    assert isinstance(retrieved, Plan)
    assert_plan_fields(retrieved, saved_plan)

    updated_plan = await repository.get_by_pk(saved_plan.pk)
    assert isinstance(updated_plan, Plan)
    assert_plan_fields(updated_plan, saved_plan)


@pytest.mark.asyncio
async def test_update_plan_without_id_raises_error(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    with pytest.raises(ValueError, match="The pk is not of type id"):
        await repository.update(default_plan)


@pytest.mark.asyncio
async def test_update_plan_with_id_non_existent_raises_error(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    default_plan._pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(PlanNotFoundError) as error:
        await repository.update(default_plan)
    assert error.value.field == "pk"
    assert error.value.value == default_plan.pk


@pytest.mark.asyncio
async def test_get_all_with_no_plans(repository: SQLAlchemyPlanRepository):
    retrieved = await repository.get_all()
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


@pytest.mark.asyncio
async def test_get_all_with_plans(
    repository: SQLAlchemyPlanRepository, 
    default_plan: Plan,
    eco_plan: Plan
):
    other_plan = Plan(name="other test plan", max_shorturls=10)

    await repository.add(default_plan)
    await repository.add(eco_plan)
    await repository.add(other_plan)

    retrieved = await repository.get_all()

    assert isinstance(retrieved, list)
    assert len(retrieved) == 3
    for i in range(len(retrieved)):
        expected_id = i + 1
        assert isinstance(retrieved[i], Plan)
        assert retrieved[i].pk.get_id() == expected_id
    assert retrieved[0].name == default_plan.name
    assert retrieved[1].name == eco_plan.name
    assert retrieved[2].name == other_plan.name


@pytest.mark.asyncio
async def test_delete_by_pk(
    repository: SQLAlchemyPlanRepository, default_plan: Plan
):
    saved_plan = await repository.add(default_plan)

    retrieved = await repository.delete_by_pk(saved_plan.pk)

    assert isinstance(retrieved, Plan)
    assert retrieved.pk.get_id() == 1
    assert retrieved.name == default_plan.name
    assert await repository.get_by_pk(saved_plan.pk) is None


@pytest.mark.asyncio
async def test_delete_by_pk_non_existent_plan_raises_error(
    repository: SQLAlchemyPlanRepository
):
    pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(PlanNotFoundError) as error:
        await repository.delete_by_pk(pk)
    assert error.value.value == pk
    assert error.value.field == "pk"
