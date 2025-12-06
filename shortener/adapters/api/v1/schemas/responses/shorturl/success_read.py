from pydantic import BaseModel

from shortener.adapters.api.v1.schemas.entities import ShortURLPrivateSchema
from shortener.domain.shorturl.shorturl import ShortURL


class ShortURLReadSuccessResponse(BaseModel):
    shorturl: ShortURLPrivateSchema

    @classmethod
    def with_shorturl(cls, shorturl: ShortURL) -> "ShortURLReadSuccessResponse":
        return cls(shorturl=ShortURLPrivateSchema.from_domain(shorturl))

    @classmethod
    def get_example(cls) -> "ShortURLReadSuccessResponse":
        return cls(shorturl=ShortURLPrivateSchema.get_example())
