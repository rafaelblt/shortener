import jwt

from datetime import timedelta

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.services.exceptions import (
    AuthTokenInvalidError,
    AuthTokenExpiredError
)
from shortener.infra.settings import settings

from shortener.domain.services.auth_token import AuthTokenService 


class JwtAuthTokenService(AuthTokenService):
    def __init__(
        self,
        secret_key: str = settings.JWT_AUTH_SECRET_KEY,
        algorithm: str = settings.JWT_AUTH_TOKEN_ALGORITHM,
        expires_minutes: int = settings.JWT_AUTH_TOKEN_EXPIRES_MINUTES
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self.expires_minutes = expires_minutes

    def generate_token(self, subject: str) -> str:
        expiration = utc_now() + timedelta(minutes=self.expires_minutes)
        payload = {"sub": subject, "exp": expiration}
        return jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                jwt=token, key=self._secret_key, algorithms=[self._algorithm]
            )
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise AuthTokenExpiredError()
        except jwt.InvalidTokenError:
            raise AuthTokenInvalidError()
