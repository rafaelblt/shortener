import pytest_asyncio

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.infra.db.repositories import SQLAlchemyUserRepository
from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork


@pytest_asyncio.fixture
async def persistent_unverified_email_user(
    persistent_default_plan: Plan,
    unverified_email_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
    sqlalchemy_user_repository: SQLAlchemyUserRepository
):
    unverified_email_user.change_plan(persistent_default_plan)
    async with sqlalchemy_uow.transaction():
        persistent_user = await sqlalchemy_user_repository.add(unverified_email_user)
    return persistent_user
