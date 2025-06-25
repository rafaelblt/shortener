from abc import ABC, abstractmethod
from typing import Optional, TypedDict

from shortener.domain.shared.language import Language
from shortener.domain.services.exceptions import MissingTemplateVariableError


class RenderResult(TypedDict):
    subject: str
    plain_body: str
    html_body: Optional[str]


class EmailTemplate(ABC):
    """Template service for emails"""
    REQUIRED_CONTEXT_VARS: list[str]

    @abstractmethod
    def render(self, lang: Language, context: dict[str, str]) -> RenderResult:
        """
        Render the email template using the provided language and context.

        Args:
            lang (Language): The language for translating the template.
            context(dict): The context to be loaded in the template.

        Returns:
            RenderResult: The TypedDict with the subject and bodies.

        Raises:
            MissingTemplateVariableError: A required variable is missing.
        """
        pass
    
    def _validate_context(self, context: dict[str, str]) -> None:
        """
        Returns `None` if the context is valid or raises 
        `MissingTemplateVariableError` if the context has missing required vars.
        """
        missing_vars = []

        for var in self.REQUIRED_CONTEXT_VARS:
            if var not in context:
                missing_vars.append(var)

        if missing_vars:
            raise MissingTemplateVariableError(missing_vars)
