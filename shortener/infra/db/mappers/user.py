from datetime import datetime

from shortener.domain.shared.datetime_utils import ensure_utc
from shortener.domain.shared.email import Email
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.user import User
from shortener.domain.user.fields import HashedPassword, Name

from shortener.infra.db.exceptions import MapperConversionError
from shortener.infra.db.mappers import map_plan_model_to_domain
from shortener.infra.db.models.user import UserModel


def map_user_domain_to_model(domain: User) -> UserModel:
    if domain.plan.pk.is_undefined():
        raise MapperConversionError(
            "The User entity needs a Plan with defined PK to be converted to UserModel."
        )
    data = {
        "id": domain.pk.get_id() if domain.pk.is_id() else None,
        "email": domain.email,
        "name": domain.name,
        "hashed_password": domain.hashed_password,
        "status": domain.status,
        "plan_id": domain.plan.pk.get_id(),
        "is_superuser": domain.is_superuser,
        "created_at": domain.created_at,
        "last_login": domain.last_login,
    }
    return UserModel(**data)


def map_user_model_to_domain(model: UserModel) -> User:
    data = {
        "pk": PrimaryKey.create_pk_id(model.id),
        "email": Email(model.email),
        "name": Name(model.name),
        "hashed_password": HashedPassword(model.hashed_password),
        "plan": map_plan_model_to_domain(model.get_plan()),
        "status": model.status,
        "is_superuser": model.is_superuser,
        "created_at": ensure_utc(model.created_at),
        "last_login": model.last_login,
    }
    if isinstance(data["last_login"], datetime):
        data["last_login"] = ensure_utc(data["last_login"])
    return User(**data)
