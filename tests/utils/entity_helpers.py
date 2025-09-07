from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared.warnings import deprecated_func

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


@deprecated_func("use pesistent plan fixtures instead")
async def get_persistent_plan(session: AsyncSession, plan: Plan):
    repository = SQLAlchemyPlanRepository(session=session)
    return await repository.add(plan)


@deprecated_func("use pesistent user fixtures instead")
async def get_persistent_user(session: AsyncSession, user: User):
    plan = user.plan
    if plan.pk.is_undefined():
        plan = await get_persistent_plan(session, plan)
    user.change_plan(plan)

    repository = SQLAlchemyUserRepository(session=session)
    return await repository.add(user)


@deprecated_func("use pesistent refresh token fixtures instead")
async def get_persistent_refresh_Token(session: AsyncSession, token: RefreshToken):
    user = token.user
    if user.pk.is_undefined():
        user = await get_persistent_user(session, user)
    token._user = user
    repository = SQLAlchemyRefreshTokenRepository(session=session)
    return await repository.add(token)


@deprecated_func("use pesistent shorturls fixtures instead")
async def get_persistent_shorturl(session: AsyncSession, shorturl: ShortURL):
    user = shorturl.owner
    if user.id is None:
        user = await get_persistent_user(session, user)
    shorturl.change_owner(user)

    repository = SQLAlchemyShortURLRepository(session=session)
    return await repository.add(shorturl)


@deprecated_func("use serialize_plan function instead")
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
    
    assert first_data == second_data, f"{first_data} != {second_data}"


@deprecated_func("use serialize_user function instead")
def assert_user_fields(
    first: User | UserModel,
    second: User | UserModel,
    ignore_pk: bool = False
):
    def define_fields(entmap, instance: User | UserModel):
        entmap["email"] = instance.email
        entmap["name"] = instance.name
        entmap["hashed_password"] = instance.hashed_password
        entmap["status"] = instance.status
        entmap["is_superuser"] = instance.is_superuser
        entmap["created_at"] = instance.created_at
        entmap["last_login"] = instance.last_login
        if isinstance(instance, User):
            entmap["pk"] = instance.pk.get_id() if instance.pk.is_id() else None
            entmap["plan_pk"] = instance.plan.pk.get_id() if instance.plan.pk.is_id() else None
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

    assert first_data == second_data, f"{first_data} != {second_data}"


@deprecated_func("use serialize_refresh_token function instead")
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
    
    assert first_data == second_data, f"{first_data} != {second_data}"


@deprecated_func("use serialize_shorturl function instead")
def assert_shorturl_fields(
    first: ShortURL | ShortURLModel,
    second: ShortURL | ShortURLModel,
    ignore_pk: bool = False
):
    def define_fields(entmap, instance):
        entmap["slug"] = instance.slug
        entmap["original_url"] = instance.original_url
        entmap["status"] = instance.status
        entmap["visit_count"] = instance.visit_count
        entmap["created_at"] = instance.created_at
        entmap["expires_at"] = instance.created_at
        entmap["last_accessed_at"] = instance.last_accessed_at
        if isinstance(instance, ShortURL):
            entmap["pk"] = instance.pk.get_id() if instance.pk.is_id() else None
        elif isinstance(instance, ShortURLModel):
            entmap["pk"] = instance.id if instance.id else None

    first_data = {}
    define_fields(first_data, first)
    second_data = {}
    define_fields(second_data, second)

    if ignore_pk:
        first_data.pop("pk")
        second_data.pop("pk")
    
    assert first_data == second_data, f"{first_data} != {second_data}"


async def serialize_plan(
    instance: Plan | PlanModel,
    exclude_fields: list[str] = []
):
    plan_dict = {}
    plan_dict["name"] = instance.name
    plan_dict["max_shorturls"] = instance.max_shorturls
    if isinstance(instance, RefreshToken):
        plan_dict["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
    elif isinstance(instance, RefreshTokenModel):
        plan_dict["pk"] = instance.id if instance.id else None
    for field in exclude_fields:
        plan_dict.pop(field)
    return plan_dict


async def serialize_user(
    instance: User | UserModel,
    exclude_fields: list[str] = []
):
    user_dict = {}
    user_dict["email"] = instance.email
    user_dict["name"] = instance.name
    user_dict["hashed_password"] = instance.hashed_password
    user_dict["status"] = instance.status
    user_dict["is_superuser"] = instance.is_superuser
    user_dict["created_at"] = instance.created_at
    user_dict["last_login"] = instance.last_login
    if isinstance(instance, User):
        user_dict["pk"] = instance.pk.get_id() if instance.pk.is_id() else None
        user_dict["plan_pk"] = instance.plan.pk.get_id() if instance.plan.pk.is_id() else None
        user_dict["shorturls"] = await instance.shorturls.get_all()
    elif isinstance(instance, UserModel):
        user_dict["pk"] = instance.id if instance.id else None
        user_dict["plan_pk"] = instance.plan_id
        user_dict["shorturls"] = list(instance.shorturls)
    for field in exclude_fields:
        user_dict.pop(field)
    return user_dict


async def serialize_refresh_token(
    instance: RefreshToken | RefreshTokenModel,
    exclude_fields: list[str] = []
):
    token_dict = {}
    token_dict["token"] = instance.token
    token_dict["expires_at"] = instance.expires_at
    token_dict["created_at"] = instance.created_at
    token_dict["revoked"] = instance.revoked
    if isinstance(instance, RefreshToken):
        token_dict["pk"] = None if instance.pk.is_undefined() else instance.pk.get_id()
        token_dict["user_pk"] = instance.user.pk.raw_value
    elif isinstance(instance, RefreshTokenModel):
        token_dict["pk"] = instance.id if instance.id else None
        token_dict["user_pk"] = str(instance.user_id)
    for field in exclude_fields:
        token_dict.pop(field)
    return token_dict


async def serialize_shorturl(
    instance: ShortURL | ShortURLModel,
    exclude_fields: list[str] = []
):
    shorturl_dict = {}
    shorturl_dict["slug"] = instance.slug
    shorturl_dict["original_url"] = instance.original_url
    shorturl_dict["status"] = instance.status
    shorturl_dict["visit_count"] = instance.visit_count
    shorturl_dict["created_at"] = instance.created_at
    shorturl_dict["expires_at"] = instance.created_at
    shorturl_dict["last_accessed_at"] = instance.last_accessed_at
    if isinstance(instance, ShortURL):
        shorturl_dict["pk"] = instance.pk.get_id() if instance.pk.is_id() else None
    elif isinstance(instance, ShortURLModel):
        shorturl_dict["pk"] = instance.id if instance.id else None
    for field in exclude_fields:
        shorturl_dict.pop(field)
    return shorturl_dict
