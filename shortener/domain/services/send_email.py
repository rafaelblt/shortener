from abc import ABC, abstractmethod
from typing import Optional

from shortener.domain.shared.email import Email


class SendEmailService(ABC):
    """Service to send emails."""

    @abstractmethod
    async def send_email(
        self, to: Email, subject: str, plain_body: str, html_body: Optional[str]
    ):
        """
        Sends an email to a recipient with both plain text and optional HTML
        content.

        Args:
            to (Email): The recipient's email address.
            subject (str): The subject of the email.
            plain_body (str): The plain text version of the email body.
            html_body (Optional[str]): The HTML version of the email body.

        Returns:
            None:
        """
        pass
