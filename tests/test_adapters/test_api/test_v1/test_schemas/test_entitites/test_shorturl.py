from shortener.adapters.api.v1.schemas.entities import PublicShortURLSchema

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL


def test_public_shorturl_from_domain(normal_shorturl: ShortURL):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    retrieved = PublicShortURLSchema.from_domain(normal_shorturl)
    
    assert retrieved.id == normal_shorturl.pk.get_id()
    assert retrieved.slug == normal_shorturl.slug
    assert retrieved.original_url == normal_shorturl.original_url
    assert retrieved.created_at == normal_shorturl.created_at
