from datetime import datetime

from shortener.domain.shared.datetime_utils import ensure_utc
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields import Slug, URL

from shortener.infra.db.models import ShortURLModel


def map_shorturl_domain_to_model(domain: ShortURL) -> ShortURLModel:
    data = {
        "id": domain.pk.get_id() if domain.pk.is_id() else None,
        "slug": domain.slug,
        "original_url": domain.original_url,
        "status": domain.status,
        "visit_count": domain.visit_count,
        "created_at": domain.created_at,
        "expires_at": domain.expires_at,
        "last_accessed_at": domain.last_accessed_at,
    }
    return ShortURLModel(**data)


def map_shorturl_model_to_domain(model: ShortURLModel) -> ShortURL:
    data = {
        "pk": PrimaryKey.create_pk_id(model.id),
        "slug": Slug(model.slug),
        "original_url": URL(model.original_url),
        "status": model.status,
        "visit_count": model.visit_count,
        "created_at": ensure_utc(model.created_at),
        "expires_at": model.expires_at,
        "last_accessed_at": model.last_accessed_at,
    }
    if isinstance(data["expires_at"], datetime):
        data["expires_at"] = ensure_utc(data["expires_at"])
    if isinstance(data["last_accessed_at"], datetime):
        data["last_accessed_at"] = ensure_utc(data["last_accessed_at"])
    return ShortURL(**data)
