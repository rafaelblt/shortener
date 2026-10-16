import pytest

from unittest.mock import NonCallableMagicMock, create_autospec

from aio_pika.abc import AbstractIncomingMessage

from shortener.use_cases.delete_shorturls_of_user import DeleteShortURLsOfUser


@pytest.fixture
def delete_shorturls_of_user() -> NonCallableMagicMock:
    use_case = create_autospec(DeleteShortURLsOfUser, instance=True)
    use_case.execute.return_value = None
    return use_case


def message_with(body: bytes) -> NonCallableMagicMock:
    """A double of a message received with the body."""
    message = create_autospec(AbstractIncomingMessage, instance=True)
    message.body = body
    return message
