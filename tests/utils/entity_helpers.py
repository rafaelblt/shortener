from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import PlanModel, UserModel, ShortURLModel

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


def assert_plan_fields(
    first: Plan | PlanModel,
    second: Plan | PlanModel,
    ignore_id: bool = False
):
    if not ignore_id:
        assert first.id == second.id
    assert first.name == second.name
    assert first.max_shorturls == second.max_shorturls


def assert_user_fields(
    first: User | UserModel,
    second: User | UserModel,
    ignore_id: bool = False
):
    first_data = {}
    first_data["id"] = first.id
    first_data["email"] = first.email
    first_data["name"] = first.name
    first_data["hashed_password"] = first.hashed_password
    first_data["status"] = first.status
    first_data["is_superuser"] = first.is_superuser
    first_data["created_at"] = first.created_at
    first_data["last_login"] = first.last_login
    if isinstance(first, User):
        first_data["plan_id"] = first.plan.id
    elif isinstance(first, UserModel):
        first_data["plan_id"] = first.plan_id
    
    second_data = {}
    second_data["id"] = second.id
    second_data["email"] = second.email
    second_data["name"] = second.name
    second_data["hashed_password"] = second.hashed_password
    second_data["status"] = second.status
    second_data["is_superuser"] = second.is_superuser
    second_data["created_at"] = second.created_at
    second_data["last_login"] = second.last_login
    if isinstance(second, User):
        second_data["plan_id"] = second.plan.id
    elif isinstance(second, UserModel):
        second_data["plan_id"] = second.plan_id

    if ignore_id:
        first_data.pop("id")
        second_data.pop("id")
    
    assert first_data == second_data


def assert_shorturl_fields(
    first: ShortURL | ShortURLModel,
    second: ShortURL | ShortURLModel,
    ignore_id: bool = False
):
    first_data = {}
    first_data["id"] = first.id
    first_data["slug"] = first.slug
    first_data["original_url"] = first.original_url
    first_data["status"] = first.status
    first_data["visit_count"] = first.visit_count
    first_data["created_at"] = first.created_at
    first_data["expires_at"] = first.expires_at
    first_data["last_accessed_at"] = first.last_accessed_at
    if isinstance(first, User):
        first_data["owner_id"] = first.owner.id
    elif isinstance(first, UserModel):
        first_data["owner_id"] = first.owner_id
    
    second_data = {}
    second_data["id"] = second.id
    second_data["slug"] = second.slug
    second_data["original_url"] = second.original_url
    second_data["status"] = second.status
    second_data["visit_count"] = second.visit_count
    second_data["created_at"] = second.created_at
    second_data["expires_at"] = second.expires_at
    second_data["last_accessed_at"] = second.last_accessed_at
    if isinstance(second, User):
        second_data["owner_id"] = second.owner.id
    elif isinstance(second, UserModel):
        second_data["owner_id"] = second.owner_id

    if ignore_id:
        first_data.pop("id")
        second_data.pop("id")
    
    assert first_data == second_data
