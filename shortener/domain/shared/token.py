from datetime import datetime, timedelta
from typing import Any, Mapping, Optional, TypedDict

from shortener.domain.shared.datetime_utils import utc_now


ExtraClaims = Mapping[str, Any]


class Token:
    def __init__(
        self,
        value: str,
        purpose: str,
        created_at: datetime,
        expires_at: datetime,
        extra_claims: Optional[ExtraClaims] = None
    ) -> None:
        self.value = value
        self.purpose = purpose
        self.created_at = created_at
        self.expires_at = expires_at
        self.extra_claims = extra_claims or {}

    @property
    def time_remaining(self) -> timedelta:
        return self.expires_at - utc_now()


class TokenDecoded(TypedDict):
    subject: str
    purpose: str
    created_at: datetime
    expires_at: datetime
    extra_claims: Optional[ExtraClaims]
