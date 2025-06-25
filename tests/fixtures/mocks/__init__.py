import pytest

from .shorturl_repository import MockShortURLRepository
from .password_hasher import MockPasswordHasherService
from .user_repository import MockUserRepository
from .plan_repository import MockPlanRepository
from .auth_token import MockAuthTokenService
from .send_email import MockSendEmailService
from .email_template import MockEmailTemplate, mock_email_template


@pytest.fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@pytest.fixture
def mock_password_hasher():
    return MockPasswordHasherService()


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()


@pytest.fixture
def mock_plan_repository():
    return MockPlanRepository()


@pytest.fixture
def mock_auth_token_service():
    return MockAuthTokenService()


@pytest.fixture
def mock_send_email_service():
    return MockSendEmailService()
