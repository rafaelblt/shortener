import jwt

from typing import Any, Mapping, Optional
from datetime import datetime, timedelta, timezone

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.services.token import TokenService, AuthTokenService, Token, TokenDecoded
from shortener.domain.services.exceptions import TokenInvalidError, TokenExpiredError

from shortener.domain.user import User, UserRepository

from shortener.infra.settings import settings


class JwtTokenService(TokenService):
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ):
        self._secret_key = secret_key or settings.jwt_secret_key
        self._algorithm = algorithm or settings.jwt_algorithm

    def generate_token(
        self,
        subject: str,
        purpose: str,
        expires_in: timedelta,
        extra_claims:  Mapping[str, Any] | None = None
    ) -> Token:
        now = utc_now().replace(microsecond=0)
        expiration = now + expires_in
        extra_claims = extra_claims or {}

        payload = {
            "sub": subject,
            "purpose": purpose,
            "exp": expiration,
            "iat": now.timestamp(),
            **extra_claims
        }
        token = jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )

        return Token(
            value=token,
            purpose=purpose,
            created_at=now,
            expires_at=expiration,
        )

    def decode_token(self, token: str):
        try:
            jwt_payload = jwt.decode(
                jwt=token, key=self._secret_key, algorithms=[self._algorithm]
            )
            exp = jwt_payload.pop("exp")
            iat = jwt_payload.pop("iat")
            return TokenDecoded(
                subject=jwt_payload.pop("sub"),
                purpose=jwt_payload.pop("purpose"),
                created_at=datetime.fromtimestamp(iat, timezone.utc),
                expires_at=datetime.fromtimestamp(exp, timezone.utc),
                extra_claims=jwt_payload
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()
