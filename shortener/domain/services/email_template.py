from abc import ABC, abstractmethod
from typing import Optional


class EmailTemplate(ABC):
    """Template service for emails"""

    @abstractmethod
    def render_subject(self, **context) -> str:
        """
        Render the subject of the email using the provided keyword arguments.
        """
        pass

    @abstractmethod
    def render_plain_body(self, **context) -> str:
        """
        Render the plain body of the email using the provided keyword arguments.
        """
        pass

    @abstractmethod
    def render_html_body(self, **context) -> Optional[str]:
        """
        Render the HTML body of the email using the provided keyword arguments.
        """
        pass
