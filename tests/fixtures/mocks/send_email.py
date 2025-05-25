from shortener.domain.services.send_email import SendEmailService


class MockSendEmailService(SendEmailService):
    def __init__(self):
        self.logs = []

    async def send_email(self, receiver: str, subject: str, body: str):
        self.logs.append(
            {"receiver": receiver, "subject": subject, "body": body}
        )
