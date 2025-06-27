import pytest

from typing import Optional, TypedDict
from shortener.domain.services.send_email import SendEmailService


class Log(TypedDict):
    to: str
    subject: str
    plain_body: str
    html_body: Optional[str]


class MockSendEmailService(SendEmailService):
    _instance = None
    mock_logs: list[Log]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "mock_logs"):
            self.mock_logs = []

    async def send_email(
        self, to: str, subject: str, plain_body: str, html_body: Optional[str]
    ):
        self.mock_logs.append({
            "to": to,
            "subject": subject,
            "plain_body": plain_body,
            "html_body": html_body
        })

    def reset(self):
        self.mock_logs.clear()


@pytest.fixture()
def mock_send_email_service():
    service = MockSendEmailService()
    service.reset()
    return service
