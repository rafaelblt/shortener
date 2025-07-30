import pytest

from shortener.infra.services.urlsafe_token import URLSafeTokenGenerator


@pytest.fixture
def generator():
    return URLSafeTokenGenerator()


def test_retrieved_token(generator: URLSafeTokenGenerator):
    token = generator.generate_token()
    assert isinstance(token, str)
