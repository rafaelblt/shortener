import pytest

from typing import Any, Mapping, TypedDict
from datetime import datetime, timedelta, timezone

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.services.token import PayloadDecoded, TokenService, TokenExpiredError, TokenInvalidError


class MockDataType(TypedDict):
    generated_tokens: list[str]


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
        purpose: TokenService.Purpose,
        expires_in: timedelta,
        extra_claims: Mapping[str, Any] | None = None
    ):
        if extra_claims is not None:
            raise NotImplementedError("extra_claims is not implemented in MockTokenService")
        expiration = utc_now() + expires_in
        token = f"{subject}|{purpose.value}|{self._secret_key}|{expiration.timestamp()}"
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
        
        return PayloadDecoded(
            subject=subject,
            purpose=purpose,
            expires_at=expiration,
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
