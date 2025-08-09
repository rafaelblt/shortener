from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL
from shortener.domain.refresh_token import RefreshToken

from shortener.infra.db.models import (
    PlanModel,
    UserModel,
    ShortURLModel,
    RefreshTokenModel
)

from shortener.infra.db.repositories import (
    SQLAlchemyPlanRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyShortURLRepository,
    SQLAlchemyRefreshTokenRepository
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


async def get_persistent_refresh_Token(session: AsyncSession, token: RefreshToken):
    user = token.user
    if user.pk.is_undefined():
        user = await get_persistent_user(session, user)
    token._user = user
    repository = SQLAlchemyRefreshTokenRepository(session=session)
    return await repository.add(token)


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
    ignore_pk: bool = False
):
    def define_fields(entmap, instance):
        entmap["pk"] = instance.pk
        entmap["slug"] = instance.slug
        entmap["original_url"] = instance.original_url
        entmap["status"] = instance.status
        entmap["visit_count"] = instance.visit_count
        entmap["created_at"] = instance.created_at
        entmap["expires_at"] = instance.created_at
        entmap["last_accessed_at"] = instance.last_accessed_at
        if isinstance(instance, ShortURL):
            entmap["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
        elif isinstance(instance, ShortURLModel):
            entmap["pk"] = instance.id if instance.id else None

    first_data = {}
    define_fields(first_data, first)
    second_data = {}
    define_fields(second_data, second)

    if ignore_pk:
        first_data.pop("pk")
        second_data.pop("pk")
    
    assert first_data == second_data
