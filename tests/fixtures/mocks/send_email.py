from shortener.domain.services.send_email import SendEmailService


class MockSendEmailService(SendEmailService):
    def __init__(self):
        self.mock_logs = []

    async def send_email(self, receiver: str, subject: str, body: str):
        self.mock_logs.append(
            {"receiver": receiver, "subject": subject, "body": body}
        )
