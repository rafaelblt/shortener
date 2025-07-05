import pytest

from typing import TypedDict

from datetime import datetime, timedelta, timezone

from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.services.auth_token import AuthTokenService
from shortener.domain.services.exceptions import (
    AuthTokenInvalidError, AuthTokenExpiredError
)


class MockDataType(TypedDict):
    generated_tokens: list[str]


class MockAuthTokenService(AuthTokenService):
    _instance = None
    mock_data: MockDataType

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.mock_data = cls._generate_mock_data()
        return cls._instance

    def __init__(self, secret_key: str = "secret123", expires_minutes: int = 60):
        self.secret_key = secret_key
        self.expires_minutes = expires_minutes

    def generate_token(self, subject: str) -> str:
        expiration = utc_now() + timedelta(minutes=self.expires_minutes)
        token = f"{subject}|{self.secret_key}|{expiration.timestamp()}"
        self.mock_data["generated_tokens"].append(token)
        return token

    def decode_token(self, token: str) -> str:
        token_split = token.split("|")

        if len(token_split) != 3:
            raise AuthTokenInvalidError()

        subject = token_split[0]
        key = token_split[1]
        expiration = datetime.fromtimestamp(float(token_split[2]), tz=timezone.utc)
        
        if key != self.secret_key:
            raise AuthTokenInvalidError()
        if utc_now() > expiration:
            raise AuthTokenExpiredError()
        
        return subject
    
    @staticmethod
    def _generate_mock_data():
        return MockDataType(generated_tokens=[])

    def reset(self):
        self.mock_data = self._generate_mock_data()


@pytest.fixture
def mock_auth_token_service():
    service = MockAuthTokenService()
    service.reset()
    return service
