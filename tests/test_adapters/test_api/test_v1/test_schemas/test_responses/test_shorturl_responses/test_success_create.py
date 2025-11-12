from shortener.adapters.api.v1.schemas.responses.shorturl import CreateShortURLSuccessResponse
from shortener.domain.shorturl import ShortURL


def test_method_with_shorturl(persistent_normal_shorturl: ShortURL):
    retrieved = CreateShortURLSuccessResponse.with_shorturl(persistent_normal_shorturl)
    assert isinstance(retrieved, CreateShortURLSuccessResponse)
    assert retrieved.shorturl.id == persistent_normal_shorturl.pk.get_id()
    assert retrieved.shorturl.slug == persistent_normal_shorturl.slug
    assert retrieved.shorturl.original_url == persistent_normal_shorturl.original_url
    assert retrieved.shorturl.created_at == persistent_normal_shorturl.created_at
