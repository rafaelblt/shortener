from shortener.domain import ShortURL


def fields_of(shorturl: ShortURL) -> dict[str, object]:
    """Every field of the short URL, to compare two of them by value."""
    return {
        "id": shorturl.id,
        "slug": shorturl.slug,
        "target_url": shorturl.target_url,
        "owner_id": shorturl.owner_id,
        "status": shorturl.status,
        "resolution_count": shorturl.resolution_count,
        "created_at": shorturl.created_at,
        "last_resolved_at": shorturl.last_resolved_at,
    }
