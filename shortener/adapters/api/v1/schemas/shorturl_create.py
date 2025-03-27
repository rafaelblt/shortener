from typing import Optional
from datetime import datetime

from shortener.domain.shorturl import Slug

from pydantic import BaseModel, ConfigDict, field_validator


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

    @classmethod
    @field_validator("custom_slug")
    def validate_custom_slug(cls, value: str):
        # TODO: not working...
        if value:
            try:
                return Slug(value)
            except Exception as e:
                raise ValueError(str(e))
        return value  
