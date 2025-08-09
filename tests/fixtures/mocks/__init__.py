import pytest

from shortener.domain.shorturl import ShortURLRepository

from .chameleon_repository import ChameleonMockRepository

from .shorturl_repository import MockShortURLRepository
from .password_hasher import MockPasswordHasherService, mock_password_hasher
from .user_repository import mock_user_repository
from .plan_repository import mock_plan_repository
from .refresh_token_repository import mock_refresh_token_repository
from .auth_token import MockAuthTokenService, mock_auth_token_service
from .token import MockTokenService, mock_token_service
from .send_email import MockSendEmailService, mock_send_email_service
from .email_template import MockEmailTemplate, mock_email_template


@pytest.fixture
def mock_shorturl_repository():
    return ChameleonMockRepository(ShortURLRepository)
