import pytest

from typing import cast

from sendgrid import SendGridAPIClient, Mail, From, Subject

from shortener.domain.services.send_email import SendEmailService
from shortener.domain.shared.email import Email

from shortener.infra.settings import settings
from shortener.infra.services.sendgrid_email import SendGridEmailService


class MockAPIClient():
    def __init__(self):
        self.mock_logs = []

    def send(self, message: Mail):
        assert isinstance(message.from_email, From)
        assert isinstance(message.subject, Subject)
        assert isinstance(message.contents, list)
        self.mock_logs.append(
            {
                "from_email": message.from_email.email,
                "to_emails": message.personalizations[0].tos[0]["email"],
                "subject": message.subject.subject,
                "plain_body": message.contents[0].content,
                "html_body": message.contents[1].content
            }
        )     


@pytest.fixture
def service():
    return SendGridEmailService()


def test_inheritance(service: SendGridEmailService):
    assert isinstance(service, SendEmailService)


def test_default_attr_from_email(service: SendGridEmailService):
    from_email = service._from_email
    assert isinstance(from_email, Email)
    assert from_email == settings.SENDGRID_FROM_EMAIL


def test_default_attr_client(service: SendGridEmailService):
    client = service._client
    assert isinstance(client, SendGridAPIClient)
    assert client.api_key == settings.SENDGRID_API_KEY


def test_custom_attr_from_email():
    service = SendGridEmailService(from_email=Email("example@gmail.com"))
    from_email = service._from_email
    assert isinstance(from_email, Email)
    assert from_email == "example@gmail.com"


def test_custom_attr_client_with_mock_client():
    service = SendGridEmailService(
        client=cast(SendGridAPIClient, MockAPIClient())
    )
    client = service._client
    assert isinstance(client, MockAPIClient)


@pytest.mark.asyncio
async def test_method_send_email_with_mock_client(normal_user):
    service = SendGridEmailService(
        client=cast(SendGridAPIClient, MockAPIClient())
    )
    await service.send_email(
        to=normal_user.email,
        subject="Subject Example",
        plain_body="Plain Content",
        html_body="HTML Content"
    )
    assert isinstance(service._client, MockAPIClient)
    assert service._client.mock_logs[0] == {
        "from_email": settings.SENDGRID_FROM_EMAIL,
        "to_emails": normal_user.email,
        "subject": "Subject Example",
        "plain_body": "Plain Content",
        "html_body": "HTML Content"
    }
