from datetime import datetime, timezone

from typing import Optional

from .slug import Slug
from .url import URL


class ShortURL:

    def __init__(
        self,
        slug: Slug,
        original_url: URL,
        id: Optional[int] = None, 
        owner_id: Optional[int] = None,
        is_active: bool = True,
        visit_count: int = 0,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        if not isinstance(slug, Slug):
            raise TypeError(
                ("The ShortURL slug must be an instance of Slug, got "
                f"{type(slug).__name__}")
            )

        if not isinstance(original_url, URL):
            raise TypeError(
                ("The ShortURL original_url must be an instance of URL, got "
                f"{type(original_url).__name__}")
            )

        if not isinstance(id, (int, type(None))):
            raise TypeError(
                ("The ShortURL id must be int or None, got "
                f"{type(id).__name__}")
            )

        if not isinstance(owner_id, (int, type(None))):
            raise TypeError(
                ("The ShortURL owner_id must be int or None, got "
                f"{type(owner_id).__name__}")
            )
        
        if not isinstance(is_active, bool):
            raise TypeError(
                ("The ShortURL is_active must be bool, got "
                f"{type(is_active).__name__}")
            )

        if not isinstance(visit_count, int):
            raise TypeError(
                ("The ShortURL visit_count must be int, got "
                f"{type(visit_count).__name__}")
            )
        
        if not isinstance(created_at, (datetime, type(None))):
            raise TypeError(
                ("The ShortURL created_at must be an instance of datetime "
                f"or None, got {type(created_at).__name__}")
            )
        
        if not isinstance(expires_at, (datetime, type(None))):
            raise TypeError(
                ("The ShortURL expires_at must be an instance of datetime "
                f"or None, got {type(expires_at).__name__}")
            )
        
        if not isinstance(last_accessed_at, (datetime, type(None))):
            raise TypeError(
                ("The ShortURL last_accessed_at must be an instance of datetime "
                f"or None, got {type(last_accessed_at).__name__}")
            )

        if visit_count < 0:
            raise TypeError(
                ("The ShortURL visit_count must be greater than or equal to 0, "
                f"got {visit_count}")
            )            
        
        self.id = id
        self.slug = slug
        self.original_url = original_url
        self.owner_id = owner_id
        self.is_active = is_active
        self.visit_count = visit_count
        self.created_at = created_at or datetime.now(tz=timezone.utc)
        self.expires_at = expires_at
        self.last_accessed_at = last_accessed_at
