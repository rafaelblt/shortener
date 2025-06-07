from typing import Optional
from shortener.domain.services.send_email import SendEmailService


class MockSendEmailService(SendEmailService):
    def __init__(self):
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
