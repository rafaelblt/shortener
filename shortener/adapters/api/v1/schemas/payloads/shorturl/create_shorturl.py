from typing import Annotated

from shortener.adapters.api.v1.validators import WrapperAfterValidator
from shortener.domain.shorturl.fields import Slug, OriginalURL

from pydantic import BaseModel, ConfigDict


class CreateShortURLPayload(BaseModel):
    original_url: Annotated[str, WrapperAfterValidator(OriginalURL)]
    custom_slug: Annotated[str, WrapperAfterValidator(Slug.validate_slug)] | None = None
    
    def convert_original_url(self) -> OriginalURL:
        return OriginalURL(self.original_url)
    
    def convert_custom_slug(self) -> Slug | None:
        if self.custom_slug:
            return Slug(self.custom_slug)
        return None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com",
                "custom_slug": "custom-slug",
            }
        }
    )
