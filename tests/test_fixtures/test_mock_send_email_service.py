import pytest

from tests.fixtures.mocks import MockSendEmailService

from shortener.domain.services.send_email import SendEmailService


def test_instance_and_inheritance(mock_send_email_service: MockSendEmailService):
    assert isinstance(mock_send_email_service, MockSendEmailService)
    assert isinstance(mock_send_email_service, SendEmailService)


@pytest.mark.asyncio
async def test_method_send_email(mock_send_email_service: MockSendEmailService):
    to = "test-receiver"
    subject = "test-subject"
    plain_body = "test body"
    html_body = "<test>body</test>"

    await mock_send_email_service.send_email(
        to=to, subject=subject, plain_body=plain_body, html_body=html_body
    )

    assert len(mock_send_email_service.mock_logs) == 1
    assert mock_send_email_service.mock_logs[0] == {
        "to": to,
        "subject": subject,
        "plain_body": plain_body,
        "html_body": html_body
    }


@pytest.mark.asyncio
async def test_logs_with_multiple_emails(mock_send_email_service: MockSendEmailService):
    to = "test-receiver"
    subject = "test-subject"
    plain_body = "test body"
    html_body = "<test>body</test>"
    
    for i in range(10):
        await mock_send_email_service.send_email(
            to=f"{to}-{i}",
            subject=f"{subject}-{i}",
            plain_body=f"{plain_body}-{i}",
            html_body=f"{html_body}-{i}"
        )
    
    assert len(mock_send_email_service.mock_logs) == 10

    for i in range(10):
        assert mock_send_email_service.mock_logs[i] == {
            "to": f"{to}-{i}",
            "subject": f"{subject}-{i}",
            "plain_body": f"{plain_body}-{i}",
            "html_body": f"{html_body}-{i}"
        }
