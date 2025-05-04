import jwt

from typing import Optional
from datetime import timedelta

from shortener.domain.shared.datetime_utils import utc_now
from shortener.infra.settings import (
    JWT_AUTH_TOKEN_EXPIRES_MINUTES, JWT_AUTH_SECRET_KEY
)

from shortener.domain.services.auth_token import AuthTokenService 


class JwtAuthTokenService(AuthTokenService):
    def __init__(
            self,
            secret_key: str = JWT_AUTH_SECRET_KEY,
            algorithm: str = "HS256",
            expires_minutes: int = JWT_AUTH_TOKEN_EXPIRES_MINUTES
        ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_minutes = expires_minutes

    def generate_token(self, subject: str) -> str:
        expiration = utc_now() + timedelta(minutes=self.expires_minutes)
        payload = {"sub": subject, "exp": expiration}
        return jwt.encode(
            payload=payload, key=self.secret_key, algorithm=self.algorithm
        )

    def decode_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(
                jwt=token, key=self.secret_key, algorithms=[self.algorithm]
            )
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
