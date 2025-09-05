import pytest
import pytest_asyncio

from shortener.domain.user.user import User
from shortener.infra.db.repositories import (
    SQLAlchemyUserRepository, SQLAlchemyPlanRepository, SQLAlchemyShortURLRepository
)


@pytest_asyncio.fixture
async def persistent_default_plan(default_plan, db_session):
    plan_repo = SQLAlchemyPlanRepository(db_session)
    return await plan_repo.add(default_plan)


@pytest_asyncio.fixture
async def persistent_eco_plan(eco_plan, db_session):
    plan_repo = SQLAlchemyPlanRepository(db_session)
    return await plan_repo.add(eco_plan)


@pytest_asyncio.fixture
async def persistent_normal_user(
    persistent_default_plan,
    normal_user: User,
    db_session
):
    user_repo = SQLAlchemyUserRepository(db_session)
    normal_user.change_plan(persistent_default_plan)
    persistent_user = await user_repo.add(normal_user)

    shorturl_repo = SQLAlchemyShortURLRepository(db_session)
    user_shorturls = await normal_user.get_shorturls()
    for sh in user_shorturls:
        persistent_sh = await shorturl_repo.add(sh)
        await persistent_user.add_shorturl(persistent_sh)

    return persistent_user


@pytest_asyncio.fixture
async def persistent_poor_user(persistent_eco_plan, poor_user, db_session):
    user_repo = SQLAlchemyUserRepository(db_session)
    poor_user.change_plan(persistent_eco_plan)
    return await user_repo.add(poor_user)


@pytest_asyncio.fixture
async def persistent_normal_shorturl(normal_shorturl, db_session):
    shorturl_repo = SQLAlchemyShortURLRepository(db_session)
    return await shorturl_repo.add(normal_shorturl)
