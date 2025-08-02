import pytest

from shortener.infra.db import get_session
from shortener.adapters.api.v1.dependencies import make_sendgrid_email_service


@pytest.fixture
def dependency_overrides(db_session, mock_send_email_service):
    return {
        get_session: lambda: db_session,
        make_sendgrid_email_service: lambda: mock_send_email_service
    }
