import pytest

from typing import Any, Mapping, TypedDict
from datetime import datetime, timedelta, timezone

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.services.token import (
    AuthTokenService, Token, TokenDecoded, TokenService, TokenExpiredError, TokenInvalidError
)
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User, UserRepository


class MockDataType(TypedDict):
    generated_tokens: list[Token]


class MockTokenService(TokenService):
    _instance = None
    mock_data: MockDataType

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.mock_data = cls._generate_mock_data()
        return cls._instance

    def __init__(self, secret_key: str = "secret123"):
        self._secret_key = secret_key

    def generate_token(
        self,
        subject: str,
        purpose: str,
        expires_in: timedelta,
        extra_claims: Mapping[str, Any] | None = None
    ):
        if extra_claims is not None:
            raise NotImplementedError("extra_claims is not implemented in MockTokenService")
        now = utc_now()
        expires_at = now + expires_in
        token_value = f"{subject}|{purpose}|{self._secret_key}|{expires_at.timestamp()}"
        token = Token(
            value=token_value,
            purpose=purpose,
            created_at=now,
            expires_at=expires_at,
            extra_claims=None
        )
        self.mock_data["generated_tokens"].append(token)
        return token

    def decode_token(self, token: str):
        token_split = token.split("|")

        if len(token_split) != 4:
            raise TokenInvalidError()

        subject = token_split[0]
        purpose = token_split[1]
        key = token_split[2]
        expiration = datetime.fromtimestamp(float(token_split[3]), tz=timezone.utc)
        
        if key != self._secret_key:
            raise TokenInvalidError()
        if utc_now() > expiration:
            raise TokenExpiredError()
        
        return TokenDecoded(
            subject=subject,
            purpose=purpose,
            extra_claims=None
        )
    
    @staticmethod
    def _generate_mock_data():
        return MockDataType(generated_tokens=[])

    def reset(self):
        self.mock_data = self._generate_mock_data()


@pytest.fixture
def mock_token_service():
    service = MockTokenService()
    service.reset()
    return service


class MockAuthTokenService(AuthTokenService):
    mock_data: MockDataType

    def __init__(
        self,
        purpose: str,
        expires_in: timedelta,
        user_repository: UserRepository,
        secret_key: str = "mock-secret-key",
    ):
        self._secret_key = secret_key
        self._purpose = purpose
        self._expires_in = expires_in
        self._user_repo = user_repository
        self.mock_data = {"generated_tokens": []}

    async def generate_token(self, user: User) -> Token:
        now = utc_now()
        expires_at = now + self._expires_in
        token_value = f"{user.pk.raw_value}|{self._purpose}|{self._secret_key}|{expires_at.timestamp()}"
        token = Token(
            value=token_value,
            purpose=self._purpose,
            created_at=now,
            expires_at=expires_at,
            extra_claims=None
        )
        self.mock_data["generated_tokens"].append(token)
        return token
    
    async def decode_token(self, token: str) -> User:
        token_split = token.split("|")

        if len(token_split) != 4:
            raise TokenInvalidError()

        subject = token_split[0]
        purpose = token_split[1]
        key = token_split[2]
        expiration = datetime.fromtimestamp(float(token_split[3]), tz=timezone.utc)
        
        if key != self._secret_key or purpose != self._purpose:
            raise TokenInvalidError()
        if utc_now() > expiration:
            raise TokenExpiredError()
        
        pk = PrimaryKey.create_pk_id(int(subject))
        user = await self._user_repo.get_by_pk(pk)
        if user is None:
            raise TokenInvalidError()
        
        return user
