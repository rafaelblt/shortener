from shortener.domain.shared.datetime_utils import ensure_utc
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.refresh_token import RefreshToken

from shortener.infra.db.models.refresh_token import RefreshTokenModel
from shortener.infra.db.mappers import map_user_model_to_domain


def map_refresh_token_domain_to_model(domain: RefreshToken) -> RefreshTokenModel:
    data = {
        "id": domain.pk.get_id() if domain.pk.is_id() else None,
        "token": domain.token,
        "revoked": domain.revoked,
        "expires_at": domain.expires_at,
        "created_at": domain.created_at,
        "user_id": domain.user.pk.get_id()
    }
    return RefreshTokenModel(**data)


def map_refresh_token_model_to_domain(model: RefreshTokenModel):
    data = {
        "pk": PrimaryKey.create_pk_id(model.id),
        "token": model.token,
        "revoked": model.revoked,
        "expires_at": ensure_utc(model.expires_at),
        "created_at": ensure_utc(model.created_at),
        "user": map_user_model_to_domain(model.get_user())
    }
    return RefreshToken(**data)
