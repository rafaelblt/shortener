from abc import ABC, abstractmethod
from typing import Optional


class EmailTemplate(ABC):
    """Template service for emails"""

    @abstractmethod
    def render_subject(self, **kwargs) -> str:
        """
        Render the subject of the email using the provided keyword arguments.
        """
        pass

    @abstractmethod
    def render_plain_body(self, **kwargs) -> str:
        """
        Render the plain body of the email using the provided keyword arguments.
        """
        pass

    @abstractmethod
    def render_html_body(self, **kwargs) -> Optional[str]:
        """
        Render the HTML body of the email using the provided keyword arguments.
        """
        pass
