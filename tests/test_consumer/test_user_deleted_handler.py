import asyncio
import logging

from datetime import timedelta
from unittest.mock import NonCallableMagicMock

import pytest

from shortener.consumer.user_deleted_handler import UserDeletedHandler
from shortener.domain import UserID
from shortener.use_cases.unavailable_error import UnavailableError
from tests.fixtures.consumer.doubles import message_with


def assert_rejected_without_requeuing(message: NonCallableMagicMock) -> None:
    message.reject.assert_awaited_once()
    # reject() doesn't requeue by default.
    assert message.reject.await_args.kwargs.get("requeue", False) is False
    message.ack.assert_not_awaited()


@pytest.fixture
def handler(delete_shorturls_of_user: NonCallableMagicMock) -> UserDeletedHandler:
    return UserDeletedHandler(delete_shorturls_of_user, retry_delay=timedelta(0))


@pytest.fixture
def message(owner_id: UserID) -> NonCallableMagicMock:
    return message_with(f'{{"user_id": "{owner_id.value}"}}'.encode())


async def test_deletes_the_shorturls_of_the_user_of_the_message(
    handler: UserDeletedHandler,
    delete_shorturls_of_user: NonCallableMagicMock,
    message: NonCallableMagicMock,
    owner_id: UserID,
):
    await handler.handle(message)
    delete_shorturls_of_user.execute.assert_awaited_once_with(owner_id.value)


async def test_acknowledges_the_message_only_after_deleting(
    handler: UserDeletedHandler,
    delete_shorturls_of_user: NonCallableMagicMock,
    message: NonCallableMagicMock,
):
    acknowledged_before_deleting: list[bool] = []
    delete_shorturls_of_user.execute.side_effect = lambda user_id: (
        acknowledged_before_deleting.append(message.ack.called)
    )

    await handler.handle(message)

    assert acknowledged_before_deleting == [False]
    message.ack.assert_awaited_once()
    message.reject.assert_not_awaited()


async def test_rejects_without_requeuing_a_message_that_is_not_the_event(
    handler: UserDeletedHandler, delete_shorturls_of_user: NonCallableMagicMock
):
    message = message_with(b'{"user_id": "not-a-uuid"}')

    await handler.handle(message)

    delete_shorturls_of_user.execute.assert_not_awaited()
    assert_rejected_without_requeuing(message)


async def test_requeues_the_message_when_the_deletion_is_unavailable(
    handler: UserDeletedHandler,
    delete_shorturls_of_user: NonCallableMagicMock,
    message: NonCallableMagicMock,
):
    delete_shorturls_of_user.execute.side_effect = UnavailableError()

    await handler.handle(message)

    message.reject.assert_awaited_once_with(requeue=True)
    message.ack.assert_not_awaited()


async def test_waits_the_retry_delay_before_requeuing(
    delete_shorturls_of_user: NonCallableMagicMock, message: NonCallableMagicMock
):
    delete_shorturls_of_user.execute.side_effect = UnavailableError()
    handler = UserDeletedHandler(
        delete_shorturls_of_user, retry_delay=timedelta(hours=1)
    )

    handling = asyncio.create_task(handler.handle(message))
    for _ in range(10):
        await asyncio.sleep(0)
    handling.cancel()
    with pytest.raises(asyncio.CancelledError):
        await handling

    delete_shorturls_of_user.execute.assert_awaited_once()
    message.reject.assert_not_awaited()


async def test_rejects_without_requeuing_when_the_deletion_raises_another_exception(
    handler: UserDeletedHandler,
    delete_shorturls_of_user: NonCallableMagicMock,
    message: NonCallableMagicMock,
):
    delete_shorturls_of_user.execute.side_effect = RuntimeError()

    await handler.handle(message)

    assert_rejected_without_requeuing(message)


async def test_logs_another_exception_of_the_deletion_as_an_error(
    handler: UserDeletedHandler,
    delete_shorturls_of_user: NonCallableMagicMock,
    message: NonCallableMagicMock,
    caplog: pytest.LogCaptureFixture,
):
    error = RuntimeError()
    delete_shorturls_of_user.execute.side_effect = error

    await handler.handle(message)

    [record] = caplog.records
    assert record.levelno == logging.ERROR
    assert record.exc_info is not None
    assert record.exc_info[1] is error
