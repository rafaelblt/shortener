from typing import Optional, Annotated

from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.exceptions import ShortURLValidationError

from pydantic import BaseModel, ConfigDict, AfterValidator


def validate_custom_slug(value: str) -> Slug:
    try:
        return Slug(value)
    except ShortURLValidationError as e:
        raise ValueError(str(e))
    

def validate_url(value: str) -> URL:
    try:
        return URL(value)
    except ShortURLValidationError as e:
        raise ValueError(str(e))


class ShortURLCreateSchema(BaseModel):
    original_url: Annotated[str, AfterValidator(validate_url)]
    custom_slug: Annotated[str, AfterValidator(validate_custom_slug)] = None
    owner_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com",
                "custom_slug": "custom-slug",
                "owner_id": 1,
            }
        }
    )
