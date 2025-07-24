import jwt

from typing import Any, Mapping, Optional
from datetime import datetime, timedelta, timezone

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.services.token import TokenService, PayloadDecoded
from shortener.domain.services.exceptions import TokenInvalidError, TokenExpiredError

from shortener.infra.settings import settings


class JwtTokenService(TokenService):
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ):
        self._secret_key = secret_key or settings.JWT_SECRET_KEY
        self._algorithm = algorithm or settings.JWT_ALGORITHM

    def generate_token(
        self,
        subject: str,
        purpose: TokenService.Purpose,
        expires_in: timedelta,
        extra_claims:  Mapping[str, Any] | None = None
    ) -> str:
        expiration = utc_now() + expires_in
        extra_claims = extra_claims or {}

        payload = {
            "sub": subject,
            "purpose": purpose,
            "exp": expiration,
            **extra_claims
        }
        return jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )

    def decode_token(self, token: str):
        try:
            jwt_payload = jwt.decode(
                jwt=token, key=self._secret_key, algorithms=[self._algorithm]
            )
            exp = jwt_payload.pop("exp")
            return PayloadDecoded(
                subject=jwt_payload.pop("sub"),
                purpose=jwt_payload.pop("purpose"),
                expires_at=datetime.fromtimestamp(exp, timezone.utc),
                extra_claims=jwt_payload
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()
