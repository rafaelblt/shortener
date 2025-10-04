import os
import pytest

from unittest.mock import patch

from fastapi.params import Depends

from shortener.infra.dependencies.fastapi.services.send_email import (
    make_sendgrid_email_service,
    get_send_email_service,
)
from shortener.infra.services.sendgrid_email import SendGridEmailService
from shortener.infra.settings import get_settings, reload_settings


def test_make_sendgrid_email_service():
    settings = get_settings()
    retrieved = make_sendgrid_email_service()
    assert isinstance(retrieved, SendGridEmailService)
    assert retrieved._from_email == settings.sendgrid_from_email
    assert retrieved._client.api_key == settings.sendgrid_api_key


@pytest.mark.parametrize(
    ["impl", "expected_dependency"],
    [
        ("passlib", make_sendgrid_email_service),
        ("", make_sendgrid_email_service),
    ]
)
def test_get_dependency_impl(impl, expected_dependency):
    with patch.dict(os.environ):
        os.environ["SEND_EMAIL_SERVICE_IMPL"] = impl
        reload_settings()
        retrieved = get_send_email_service()
        assert isinstance(retrieved, Depends)
        assert retrieved.dependency == expected_dependency
