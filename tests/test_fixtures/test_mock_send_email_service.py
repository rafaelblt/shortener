import pytest

from tests.fixtures import MockSendEmailService

from shortener.domain.services.send_email import SendEmailService


def test_instance_and_inheritance(mock_send_email_service: MockSendEmailService):
    assert isinstance(mock_send_email_service, MockSendEmailService)
    assert isinstance(mock_send_email_service, SendEmailService)


@pytest.mark.asyncio
async def test_method_send_email(mock_send_email_service: MockSendEmailService):
    receiver = "test-receiver"
    subject = "test-subject"
    body = "test-body"

    await mock_send_email_service.send_email(
        receiver=receiver, subject=subject, body=body
    )

    assert len(mock_send_email_service.logs) == 1
    assert mock_send_email_service.logs[0] == {
        "receiver": receiver, "subject": subject, "body": body
    }


@pytest.mark.asyncio
async def test_logs_with_multiple_emails(mock_send_email_service: MockSendEmailService):
    receiver = "test-receiver"
    subject = "test-subject"
    body = "test-body"
    
    for i in range(10):
        await mock_send_email_service.send_email(
            receiver=f"{receiver}-{i}",
            subject=f"{subject}-{i}",
            body=f"{body}-{i}"
        )
    
    assert len(mock_send_email_service.logs) == 10

    for i in range(10):
        assert mock_send_email_service.logs[i] == {
            "receiver": f"{receiver}-{i}",
            "subject": f"{subject}-{i}",
            "body": f"{body}-{i}"
        }
