from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL
from shortener.domain.refresh_token import RefreshToken

from shortener.infra.db.models import PlanModel, UserModel, ShortURLModel, RefreshTokenModel

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
    if plan.pk.is_undefined():
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
    ignore_pk: bool = False
):
    def define_fields(entmap, instance: Plan | PlanModel):
        entmap["name"] = instance.name
        entmap["max_shorturls"] = instance.max_shorturls
        if isinstance(instance, RefreshToken):
            entmap["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
        elif isinstance(instance, RefreshTokenModel):
            entmap["pk"] = instance.id if instance.id else None

    first_data = {}
    define_fields(first_data, first)
    second_data = {}
    define_fields(second_data, second)

    if ignore_pk:
        first_data.pop("pk")
        second_data.pop("pk")
    
    assert first_data == second_data


def assert_user_fields(
    first: User | UserModel,
    second: User | UserModel,
    ignore_pk: bool = False
):
    def define_fields(entmap, instance: User | UserModel):
        entmap = {}
        entmap["email"] = instance.email
        entmap["name"] = instance.name
        entmap["hashed_password"] = instance.hashed_password
        entmap["status"] = instance.status
        entmap["is_superuser"] = instance.is_superuser
        entmap["created_at"] = instance.created_at
        entmap["last_login"] = instance.last_login
        if isinstance(instance, User):
            if instance.plan.pk.is_undefined():
                plan_pk = None
            else:
                plan_pk = instance.plan.pk.get_id()
            entmap["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
            entmap["plan_pk"] = plan_pk
        elif isinstance(instance, UserModel):
            entmap["pk"] = instance.id if instance.id else None
            entmap["plan_pk"] = instance.plan_id
    
    first_data = {}
    define_fields(first_data, first)
    second_data = {}
    define_fields(second_data, second)

    if ignore_pk:
        first_data.pop("pk")
        second_data.pop("pk")
    
    assert first_data == second_data


def assert_refresh_token_fields(
    first: RefreshToken | RefreshTokenModel,
    second: RefreshToken | RefreshTokenModel,
    ignore_pk: bool = False
):
    def define_fields(entmap, instance):
        entmap["token"] = instance.token
        entmap["expires_at"] = instance.expires_at
        entmap["created_at"] = instance.created_at
        entmap["revoked"] = instance.revoked
        if isinstance(instance, RefreshToken):
            entmap["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
            entmap["user_pk"] = instance.user.pk.raw_value
        elif isinstance(instance, RefreshTokenModel):
            entmap["pk"] = instance.id if instance.id else None
            entmap["user_pk"] = str(instance.user_id)

    first_data = {}
    define_fields(first_data, first)
    second_data = {}
    define_fields(second_data, second)

    if ignore_pk:
        first_data.pop("pk")
        second_data.pop("pk")
    
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
