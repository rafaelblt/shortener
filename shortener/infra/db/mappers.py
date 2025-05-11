from datetime import datetime

from shortener.domain.shared.datetime_utils import ensure_utc

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


def map_plan_domain_to_model(domain: Plan) -> PlanModel:
    return PlanModel(
        id=domain.id,
        name=domain.name,
        max_shorturls=domain.max_shorturls
    )


def map_user_model_to_domain(model: UserModel) -> User:
    data = {
        "id": model.id,
        "email": Email(model.email),
        "name": Name(model.name),
        "hashed_password": HashedPassword(model.hashed_password),
        "plan": map_plan_model_to_domain(model.get_plan()),
        "shorturls_count": model.shorturls_count,
        "status": model.status,
        "is_superuser": model.is_superuser,
        "created_at": model.created_at,
        "last_login": model.last_login,
    }

    if isinstance(data["created_at"], datetime):
        data["created_at"] = ensure_utc(data["created_at"])
    if isinstance(data["last_login"], datetime):
        data["last_login"] = ensure_utc(data["last_login"])
    
    return User(**data)


def map_user_domain_to_model(domain: User) -> UserModel:
    data = {
        "id": domain.id,
        "email": domain.email,
        "name": domain.name,
        "hashed_password": domain.hashed_password,
        "status": domain.status,
        "plan_id": domain.plan.id,
        "shorturls_count": domain.shorturls_count,
        "is_superuser": domain.is_superuser,
        "created_at": domain.created_at,
        "last_login": domain.last_login,
    }

    if not isinstance(data["plan_id"], int):
        raise TypeError("User needs a Plan with ID to be converted to UserModel.")
    
    return UserModel(**data)


def map_shorturl_model_to_domain(model: ShortURLModel) -> ShortURL:
    data = {
        "id": model.id,
        "slug": Slug(model.slug),
        "original_url": URL(model.original_url),
        "owner": map_user_model_to_domain(model.get_owner()),
        "status": model.status,
        "visit_count": model.visit_count,
        "created_at": model.created_at,
        "expires_at": model.expires_at,
        "last_accessed_at": model.last_accessed_at,
    }

    if isinstance(data["created_at"], datetime):
        data["created_at"] = ensure_utc(data["created_at"])
    if isinstance(data["expires_at"], datetime):
        data["expires_at"] = ensure_utc(data["expires_at"])
    if isinstance(data["last_accessed_at"], datetime):
        data["last_accessed_at"] = ensure_utc(data["last_accessed_at"])

    return ShortURL(**data)


def map_shorturl_domain_to_model(domain: ShortURL) -> ShortURLModel:
    data = {
        "id": domain.id,
        "slug": domain.slug,
        "original_url": domain.original_url,
        "owner_id": domain.owner.id,
        "status": domain.status,
        "visit_count": domain.visit_count,
        "created_at": domain.created_at,
        "expires_at": domain.expires_at,
        "last_accessed_at": domain.last_accessed_at,
    }

    if not isinstance(data["owner_id"], int):
        raise TypeError(
            "ShortURL needs a User with ID to be converted to ShortURLModel."
        )
    
    return ShortURLModel(**data)
