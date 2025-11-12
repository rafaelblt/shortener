from pydantic import BaseModel

from shortener.adapters.api.v1.schemas.entities import PublicShortURLSchema
from shortener.domain.shorturl import ShortURL


class CreateShortURLSuccessResponse(BaseModel):
    shorturl: PublicShortURLSchema

    @classmethod
    def with_shorturl(cls, shorturl: ShortURL) -> "CreateShortURLSuccessResponse":
        return cls(shorturl=PublicShortURLSchema.from_domain(shorturl))
