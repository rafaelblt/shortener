from abc import ABC, abstractmethod


class EmailTemplateRenderer(ABC):
    """Template renderer service for emails"""

    @abstractmethod
    def render_subject(self, **kwargs) -> str:
        """
        Render the subject of the email using the provided keyword arguments.
        """
        pass

    @abstractmethod
    def render_body(self, **kwargs) -> str:
        """
        Render the body of the email using the provided keyword arguments.
        """
        pass
