from typing import Optional

from sendgrid import SendGridAPIClient, Mail, Content

from shortener.infra.settings import settings

from shortener.domain.shared.email import Email
from shortener.domain.services.send_email import SendEmailService


class SendGridEmailService(SendEmailService):
    """SendEmailService implementation with SendGrid"""

    def __init__(
        self,
        from_email = Email(settings.sendgrid_from_email),
        client = SendGridAPIClient(settings.sendgrid_api_key)
    ):
        """
        Args:
            from_email (Email): The email sender.
            client (SendGridAPIClient): SendGrid client instance.
        """
        self._from_email = from_email
        self._client = client

    async def send_email(
        self, to: Email, subject: str, plain_body: str, html_body: Optional[str]
    ) -> None:
        message = Mail(
            from_email=self._from_email,
            to_emails=to,
            subject=subject
        )

        message.add_content(Content("text/plain", plain_body))
        if html_body:
            message.add_content(Content("text/html", html_body))

        self._client.send(message)
