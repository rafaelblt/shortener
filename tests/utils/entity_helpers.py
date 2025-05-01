from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL

from shortener.infra.db.repositories import (
    SQLAlchemyPlanRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyShortURLRepository
)


async def get_persistent_plan(session: AsyncSession, plan: Plan):
    repository = SQLAlchemyPlanRepository(session=session)
    return await repository.add(plan)


async def get_persistent_user(session: AsyncSession, user: User):
    plan = user.plan
    if plan.id is None:
        plan = await get_persistent_plan(session, plan)
    user.change_plan(plan)

    repository = SQLAlchemyUserRepository(session=session)
    return await repository.add(user)


async def get_persistent_shorturl(session: AsyncSession, shorturl: ShortURL):
    user = shorturl.user
    if user.id is None:
        user = await get_persistent_user(session, user)
    shorturl.change_owner(user)

    repository = SQLAlchemyShortURLRepository(session=session)
    return await repository.add(shorturl)
