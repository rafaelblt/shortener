from abc import ABC, abstractmethod
from typing import Optional

from shortener.domain.services.exceptions import MissingTemplateVariableError


class EmailTemplate(ABC):
    """Template service for emails"""
    REQUIRED_CONTEXT_VARS: list[str]

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

    def _get_context(self, **kwargs) -> dict[str, str]:
        context = {}
        missing_vars = []
        for field in self.REQUIRED_CONTEXT_VARS:
            try:
                context[field] = kwargs.pop(field)
            except KeyError:
                missing_vars.append(field)
        if missing_vars:
            raise MissingTemplateVariableError(missing_vars)
        for extra_field in kwargs:
            try:
                context[extra_field] = kwargs.get(extra_field)
            except KeyError:
                continue
        return context
