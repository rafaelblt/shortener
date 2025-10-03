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


class JwtAuthTokenService(AuthTokenService):
    def __init__(
        self,
        user_repository: UserRepository,
        purpose: str,
        expires_in: timedelta,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ):
        self._user_repo = user_repository
        self._purpose = purpose
        self._expires_in = expires_in
        self._jwt_service = JwtTokenService(secret_key, algorithm)

    async def generate_token(self, user: User) -> Token:
        return self._jwt_service.generate_token(
            subject=user.pk.raw_value,
            purpose=self._purpose,
            expires_in=self._expires_in
        )
    
    async def decode_token(self, token: str) -> User:
        payload = self._jwt_service.decode_token(token)

        try:
            pk = PrimaryKey.create_pk_id(int(payload["subject"]))
        except (ValueError, TypeError):
            raise TokenInvalidError()
        
        if payload["purpose"] != self._purpose:
            raise TokenInvalidError()

        user = await self._user_repo.get_by_pk(pk)
        if user is None:
            raise TokenInvalidError()
        
        return user
