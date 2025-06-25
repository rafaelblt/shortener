import pytest

from shortener.domain.shared.language import Language
from shortener.domain.services.email_template import EmailTemplate, RenderResult


class MockEmailTemplate(EmailTemplate):
    REQUIRED_CONTEXT_VARS = []

    def render(self, lang: Language, context: dict[str, str]) -> RenderResult:
        return RenderResult(
            subject=f"{lang} => Verification Email",
            plain_body=f"Plain text ({lang}): {context}",
            html_body=f"<html> <{lang}> <{context}> </html>"
        )


@pytest.fixture
def mock_email_template():
    return MockEmailTemplate()
