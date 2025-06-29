import pytest

from shortener.infra.db import get_session
from shortener.infra.services.sendgrid_email import SendGridEmailService


@pytest.fixture
def dependency_overrides(db_session, mock_send_email_service):
    return {
        get_session: lambda: db_session,
        SendGridEmailService: lambda: mock_send_email_service
    }
