from shortener.domain.plan import Plan

from shortener.domain.user import User
from shortener.domain.user.fields import Email, Name, HashedPassword

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL

from shortener.infra.db.models import UserModel, ShortURLModel, PlanModel
    

def map_plan_model_to_domain(model: PlanModel) -> Plan:
    return Plan(
        id=model.id,
        name=model.name,
        max_shorturls=model.max_shorturls
    )


def map_user_model_to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        name=Name(model.name),
        hashed_password=HashedPassword(model.hashed_password),
        plan=map_plan_model_to_domain(model.plan),
        shorturls_count=len(model.shorturls),
        status=model.status,
        is_superuser=model.is_superuser,
        created_at=model.created_at,
        last_login=model.last_login,
    )


def map_user_domain_to_model(domain: User) -> UserModel:
    return UserModel(
        id=domain.id,
        email=domain.email,
        name=domain.name,
        hashed_password=domain.hashed_password,
        status=domain.status,
        is_superuser=domain.is_superuser,
        created_at=domain.created_at,
        last_login=domain.last_login,
    )


def map_shorturl_model_to_domain(model: ShortURLModel) -> ShortURL:
    return ShortURL(
        id=model.id,
        slug=Slug(model.slug),
        original_url=URL(model.original_url),
        owner=map_user_model_to_domain(model.owner),
        status=model.status,
        visit_count=model.visit_count,
        created_at=model.created_at,
        expires_at=model.expires_at,
        last_accessed_at=model.last_accessed_at,
    )


def map_shorturl_domain_to_model(domain: ShortURL) -> ShortURLModel:
    return ShortURLModel(
        id=domain.id,
        slug=domain.slug,
        original_url=domain.original_url,
        owner_id=domain.owner.id,
        status=domain.status,
        visit_count=domain.visit_count,
        created_at=domain.created_at,
        expires_at=domain.expires_at,
        last_accessed_at=domain.last_accessed_at,
    )
