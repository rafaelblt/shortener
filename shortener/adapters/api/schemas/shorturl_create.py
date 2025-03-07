from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShortURLCreateSchema(BaseModel):
    original_url: str
    custom_slug: Optional[str] = None
    owner_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com",
                "custom_slug": "custom-slug",
                "owner_id": 1,
                "expires_at": "2023-12-31T23:59:59"
            }
        }
    )
