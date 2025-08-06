import pytest

from shortener.infra.db import get_session
from shortener.adapters.api.v1.dependencies import (
    make_sendgrid_email_service,
    make_passlib_password_hasher
)


@pytest.fixture
def dependency_overrides(
    db_session, mock_send_email_service, wrapper_passlib_password_hasher
):
    return {
        get_session: lambda: db_session,
        make_sendgrid_email_service: lambda: mock_send_email_service,
        make_passlib_password_hasher: lambda: wrapper_passlib_password_hasher
    }
