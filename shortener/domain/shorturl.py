from datetime import datetime, timezone

from typing import Optional


class ShortURL:
    def __init__(
        self,
        slug: str,
        original_url: str,
        owner_id: Optional[int] = None,
        is_active: bool = True,
        visit_count: int = 0,
        created_at: datetime = datetime.now(tz=timezone.utc),
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        self.slug = slug
        self.original_url = original_url
        self.owner_id = owner_id
        self.is_active = is_active
        self.visit_count = visit_count
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_accessed_at = last_accessed_at
