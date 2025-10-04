import pytest

from shortener.infra.db import get_session
from shortener.infra.dependencies.fastapi.services.send_email import make_sendgrid_email_service
from shortener.infra.dependencies.fastapi.services.password_hasher import make_passlib_password_hasher_service


@pytest.fixture
def dependency_overrides(
    db_session, mock_send_email_service, wrapper_passlib_password_hasher
):
    return {
        get_session: lambda: db_session,
        make_sendgrid_email_service: lambda: mock_send_email_service,
        make_passlib_password_hasher_service: lambda: wrapper_passlib_password_hasher
    }
