from abc import ABC, abstractmethod
from typing import Optional

from shortener.domain.shared.language import Language
from shortener.domain.services.exceptions import MissingTemplateVariableError


class EmailTemplate(ABC):
    """Template service for emails"""
    REQUIRED_CONTEXT_VARS: list[str]

    @abstractmethod
    def render_subject(self, lang: Language, context: dict[str, str]) -> str:
        """
        Render the subject of the email using the provided language and context.
        """
        pass

    @abstractmethod
    def render_plain_body(self, lang: Language, context: dict[str, str]) -> str:
        """
        Render the plain body of the email using the provided language and context.
        """
        pass

    @abstractmethod
    def render_html_body(self, lang: Language, context: dict[str, str]) -> Optional[str]:
        """
        Render the HTML body of the email using the provided language and context.
        """
        pass

    def process_context(self, context: dict[str, str]) -> dict[str, str]:
        processed_ctx = {}
        missing_vars = []
        input_ctx = context.copy()

        for var in self.REQUIRED_CONTEXT_VARS:
            try:
                processed_ctx[var] = input_ctx.pop(var)
            except KeyError:
                missing_vars.append(var)
        
        if missing_vars:
            raise MissingTemplateVariableError(missing_vars)
        
        for extra_var in input_ctx:
            try:
                processed_ctx[extra_var] = input_ctx.get(extra_var)
            except KeyError:
                continue
        
        return processed_ctx
