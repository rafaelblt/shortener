import pytest

from .shorturl_repository import MockShortURLRepository
from .password_hasher import MockPasswordHasherService, mock_password_hasher
from .user_repository import MockUserRepository
from .plan_repository import MockPlanRepository
from .auth_token import MockAuthTokenService, mock_auth_token_service
from .token import MockTokenService, mock_token_service
from .send_email import MockSendEmailService, mock_send_email_service
from .email_template import MockEmailTemplate, mock_email_template


@pytest.fixture
def mock_shorturl_repository():
    return MockShortURLRepository()


@pytest.fixture
def mock_user_repository():
    return MockUserRepository()


@pytest.fixture
def mock_plan_repository():
    return MockPlanRepository()
