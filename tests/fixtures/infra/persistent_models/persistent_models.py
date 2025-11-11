import pytest
import pytest_asyncio

from shortener.domain.plan import Plan
from shortener.domain.user import User

from shortener.infra.db.repositories import (
    SQLAlchemyUserRepository, SQLAlchemyPlanRepository, SQLAlchemyShortURLRepository
)
from shortener.infra.services.refresh_token import SQLAlchemyRefreshAuthTokenService
from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork



@pytest_asyncio.fixture
async def persistent_default_plan(
    default_plan,
    sqlalchemy_plan_repository: SQLAlchemyPlanRepository,
    sqlalchemy_uow: SQLAlchemyUnitOfWork
):
    async with sqlalchemy_uow.transaction():
        persistent_plan = await sqlalchemy_plan_repository.add(default_plan)
    return persistent_plan


@pytest_asyncio.fixture
async def persistent_eco_plan(
    eco_plan,
    sqlalchemy_plan_repository: SQLAlchemyPlanRepository,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    async with sqlalchemy_uow.transaction():
        persistent_plan = await sqlalchemy_plan_repository.add(eco_plan)
    return persistent_plan


@pytest_asyncio.fixture
async def persistent_normal_user(
    persistent_default_plan,
    persistent_normal_shorturl,
    normal_user: User,
    sqlalchemy_user_repository: SQLAlchemyUserRepository,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
):
    normal_user.change_plan(persistent_default_plan)
    async with sqlalchemy_uow.transaction():
        persistent_user = await sqlalchemy_user_repository.add(normal_user)
        await persistent_user.add_shorturl(persistent_normal_shorturl)

    return persistent_user


@pytest_asyncio.fixture
async def persistent_poor_user(
    persistent_eco_plan,
    poor_user,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
    sqlalchemy_user_repository: SQLAlchemyUserRepository
):
    poor_user.change_plan(persistent_eco_plan)
    async with sqlalchemy_uow.transaction():
        persistent_user = await sqlalchemy_user_repository.add(poor_user)
    return persistent_user


@pytest_asyncio.fixture
async def persistent_banned_user(
    persistent_default_plan: Plan,
    banned_user: User,
    sqlalchemy_uow: SQLAlchemyUnitOfWork,
    sqlalchemy_user_repository: SQLAlchemyUserRepository
):
    banned_user.change_plan(persistent_default_plan)
    async with sqlalchemy_uow.transaction():
        persistent_user = await sqlalchemy_user_repository.add(banned_user)
    return persistent_user


@pytest_asyncio.fixture
async def persistent_normal_shorturl(
    normal_shorturl,
    sqlalchemy_shorturl_repository: SQLAlchemyShortURLRepository,
    sqlalchemy_uow: SQLAlchemyUnitOfWork
):
    async with sqlalchemy_uow.transaction():
        persistent_shorturl = await sqlalchemy_shorturl_repository.add(normal_shorturl)
    return persistent_shorturl



