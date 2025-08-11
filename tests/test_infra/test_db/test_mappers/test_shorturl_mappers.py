from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import ShortURLModel
from shortener.infra.db.mappers import (
    map_shorturl_model_to_domain, map_shorturl_domain_to_model
)

from tests.utils.entity_helpers import assert_shorturl_fields


def test_map_shorturl_domain_to_model(normal_shorturl: ShortURL):
    retrieved = map_shorturl_domain_to_model(normal_shorturl)
    assert isinstance(retrieved, ShortURLModel)
    assert_shorturl_fields(retrieved, normal_shorturl)


def test_map_shorturl_model_to_domain(normal_shorturl: ShortURL):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    shorturl_model = map_shorturl_domain_to_model(normal_shorturl)

    retrieved = map_shorturl_model_to_domain(shorturl_model)

    assert isinstance(retrieved, ShortURL)
    assert_shorturl_fields(retrieved, normal_shorturl)
