import pytest

from shortener.domain.plan import Plan

from shortener.infra.db.models import PlanModel
from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork
from shortener.infra.db.mappers import map_plan_domain_to_model


def test_init(sqlalchemy_session):
    retrieved = SQLAlchemyUnitOfWork(sqlalchemy_session)
    assert retrieved.session == sqlalchemy_session


@pytest.mark.asyncio
async def test_method_transaction(sqlalchemy_uow: SQLAlchemyUnitOfWork):
    async with sqlalchemy_uow.transaction() as uow:
        assert uow == sqlalchemy_uow
        assert uow.session.in_transaction()


@pytest.mark.asyncio
async def test_commit_after_transaction_finished(
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
    default_plan: Plan
):
    default_plan_model = map_plan_domain_to_model(default_plan)
    async with sqlalchemy_uow.transaction() as uow:
        uow.session.add(default_plan_model)
        await uow.session.flush()
        await uow.session.refresh(default_plan_model)
    found = await sqlalchemy_uow.session.get(PlanModel, 1)
    assert found


@pytest.mark.asyncio
async def test_rollback_after_exception_in_transaction(
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
    default_plan: Plan
):
    default_plan_model = map_plan_domain_to_model(default_plan)
    try:
        async with sqlalchemy_uow.transaction() as uow:
            uow.session.add(default_plan_model)
            await uow.session.flush()
            await uow.session.refresh(default_plan_model)
            raise Exception()
    except:
        pass
    found = await sqlalchemy_uow.session.get(PlanModel, 1)
    assert found is None
