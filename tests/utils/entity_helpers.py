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
    user = shorturl.owner
    if user.id is None:
        user = await get_persistent_user(session, user)
    shorturl.change_owner(user)

    repository = SQLAlchemyShortURLRepository(session=session)
    return await repository.add(shorturl)


def assert_shorturl_fields(
    first: ShortURL, second: ShortURL, ignore_id: bool = False
):
    if not ignore_id:
        assert first.id == second.id
    assert first.slug == second.slug
    assert first.original_url == second.original_url
    assert first.owner.id == second.owner.id
    assert first.status == second.status
    assert first.visit_count == second.visit_count
    assert first.created_at == second.created_at
    assert first.expires_at == second.expires_at
    assert first.last_accessed_at == second.last_accessed_at
